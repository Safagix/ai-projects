from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import lancedb

from .config import settings

BGE_MODEL_ID = "bge-m3"
ACTIVE_INDEX_NAME = "rag_bge_m3"
INDEX_TABLE_PREFIX = "rag_bge_m3_index_"


class SemanticUnavailable(RuntimeError):
    pass


class SemanticReindexCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticResult:
    title: str
    source: str
    excerpt: str
    score: float
    source_page: int | None
    chunk_number: int | None
    chunk_id: str


@dataclass(frozen=True)
class SemanticIndexBuild:
    table_name: str | None
    source_count: int


class BgeM3Embedder:
    def __init__(self) -> None:
        self.model_path = settings.project_root / "models" / "embeddings" / BGE_MODEL_ID
        self._model: Any | None = None

    def ensure_available(self) -> None:
        if not self.model_path.is_dir() or not any(self.model_path.iterdir()):
            raise SemanticUnavailable("BGE-M3 no está descargado. Ejecutar benchmark y descarga verificada antes de activar búsqueda semántica.")
        try:
            from FlagEmbedding import BGEM3FlagModel  # noqa: F401
        except ImportError as exc:
            raise SemanticUnavailable("El runtime FlagEmbedding no está disponible.") from exc

    def _load(self) -> Any:
        self.ensure_available()
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel

            self._model = BGEM3FlagModel(str(self.model_path), use_fp16=False, devices="cpu")
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._load().encode_corpus(
            texts, batch_size=1, max_length=1024, return_dense=True, return_sparse=False, return_colbert_vecs=False
        )
        return result["dense_vecs"].tolist()

    def embed_query(self, text: str) -> list[float]:
        result = self._load().encode_queries(
            [text], batch_size=1, max_length=512, return_dense=True, return_sparse=False, return_colbert_vecs=False
        )
        return result["dense_vecs"][0].tolist()


def stable_chunk_id(row: dict[str, Any]) -> str:
    content = " ".join(str(row["content"]).split())
    identity = "\0".join(
        [
            str(row["source"]),
            str(row.get("source_page") or ""),
            str(row.get("chunk_number") or 1),
            str(row["title"]),
            content,
        ]
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


class LanceSemanticStore:
    def __init__(self, table_name: str | None = None) -> None:
        self.db_path: Path = settings.lancedb_dir
        self.table_name = table_name

    def _db(self):
        self.db_path.mkdir(parents=True, exist_ok=True)
        return lancedb.connect(str(self.db_path))

    @staticmethod
    def _has_table(db: Any, table_name: str) -> bool:
        # table_exists currently delegates to unsupported namespace operations for local LanceDB 0.38.
        return table_name in db.list_tables().tables

    @staticmethod
    def staging_table_name(job_id: str) -> str:
        return f"{INDEX_TABLE_PREFIX}{job_id.replace('-', '')}"

    def build(
        self,
        rows: list[dict[str, Any]],
        *,
        job_id: str,
        embedder: BgeM3Embedder,
        should_cancel: Callable[[], bool],
        on_progress: Callable[[int, int], None],
    ) -> SemanticIndexBuild:
        if not rows:
            return SemanticIndexBuild(table_name=None, source_count=0)
        db = self._db()
        table_name = self.staging_table_name(job_id)
        if self._has_table(db, table_name):
            db.drop_table(table_name, ignore_missing=True)
        table = None
        try:
            for number, row in enumerate(rows, start=1):
                if should_cancel():
                    raise SemanticReindexCancelled("La reindexación fue cancelada.")
                vector = embedder.embed_documents([row["content"]])[0]
                record = {
                    "chunk_id": stable_chunk_id(row),
                    "title": row["title"],
                    "source": row["source"],
                    "source_page": row.get("source_page"),
                    "chunk_number": row.get("chunk_number") or 1,
                    "content": row["content"],
                    "vector": vector,
                }
                if table is None:
                    table = db.create_table(table_name, data=[record])
                else:
                    table.add([record])
                on_progress(number, len(rows))
            return SemanticIndexBuild(table_name=table_name, source_count=len(rows))
        except Exception:
            db.drop_table(table_name, ignore_missing=True)
            raise

    def search(self, vector: list[float], limit: int) -> list[SemanticResult]:
        if not self.table_name:
            return []
        db = self._db()
        if not self._has_table(db, self.table_name):
            return []
        rows = db.open_table(self.table_name).search(vector).limit(limit).to_list()
        return [
            SemanticResult(
                title=row["title"],
                source=row["source"],
                excerpt=row["content"][:320],
                score=float(row.get("_distance", 0.0)),
                source_page=int(row["source_page"]) if row.get("source_page") is not None else None,
                chunk_number=int(row["chunk_number"]) if row.get("chunk_number") is not None else None,
                chunk_id=row["chunk_id"],
            )
            for row in rows
        ]

    def count(self) -> int:
        if not self.table_name:
            return 0
        db = self._db()
        return int(db.open_table(self.table_name).count_rows()) if self._has_table(db, self.table_name) else 0

    def drop_managed_table(self, table_name: str | None) -> None:
        if not table_name or not table_name.startswith(INDEX_TABLE_PREFIX):
            return
        self._db().drop_table(table_name, ignore_missing=True)


def semantic_reindex(
    rows: list[dict[str, Any]],
    *,
    job_id: str,
    should_cancel: Callable[[], bool],
    on_progress: Callable[[int, int], None],
) -> SemanticIndexBuild:
    embedder = BgeM3Embedder()
    embedder.ensure_available()
    return LanceSemanticStore().build(
        rows, job_id=job_id, embedder=embedder, should_cancel=should_cancel, on_progress=on_progress
    )


def semantic_search(query: str, table_name: str | None, limit: int = 8) -> list[SemanticResult]:
    if not table_name:
        return []
    return LanceSemanticStore(table_name=table_name).search(BgeM3Embedder().embed_query(query), limit)
