"""Index Markdown files into SQLite with embeddings stored as numpy blobs."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from local_rag.chunking import Chunk, chunk_markdown
from local_rag.config import settings
from local_rag.db import get_connection, init_db
from local_rag.ollama_client import OllamaClient


@dataclass
class IndexedDocument:
    path: Path
    title: str
    file_hash: str
    file_size_bytes: int
    modified_at: float
    chunks: list[Chunk]


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def embedding_to_blob(vec: list[float]) -> bytes:
    arr = np.array(vec, dtype=np.float32)
    arr = _normalize(arr)
    return arr.tobytes()


def blob_to_embedding(blob: bytes) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.float32)
    if arr.size == 0:
        return arr
    return _normalize(arr)


def _matches_any(path: Path, patterns: tuple[str, ...]) -> bool:
    as_posix = path.as_posix()
    return any(fnmatch.fnmatch(as_posix, p) for p in patterns)


def discover_markdown_files(paths: list[str] | None = None) -> list[Path]:
    roots = [Path(p) for p in (paths or list(settings.rag_knowledge_dirs))]
    files: list[Path] = []

    for root in roots:
        if root.is_file() and root.suffix.lower() == ".md":
            if not _matches_any(root, settings.rag_exclude_globs):
                files.append(root.resolve())
            continue
        if not root.exists():
            continue
        for pattern in settings.rag_include_globs:
            for candidate in root.glob(pattern):
                if not candidate.is_file():
                    continue
                resolved = candidate.resolve()
                if _matches_any(resolved, settings.rag_exclude_globs):
                    continue
                files.append(resolved)

    return sorted(set(files))


def load_document(path: Path) -> IndexedDocument:
    content = path.read_text(encoding="utf-8", errors="ignore")
    stat = path.stat()
    chunks = chunk_markdown(
        content,
        max_chars=settings.rag_chunk_max_chars,
        overlap=settings.rag_chunk_overlap,
    )
    file_hash = hashlib.sha256(content.encode("utf-8", "ignore")).hexdigest()
    return IndexedDocument(
        path=path,
        title=path.stem,
        file_hash=file_hash,
        file_size_bytes=stat.st_size,
        modified_at=stat.st_mtime,
        chunks=chunks,
    )


def ingest_paths(paths: list[str] | None = None, *, max_files: int | None = None) -> dict[str, int]:
    init_db()
    client = OllamaClient()
    files = discover_markdown_files(paths)
    if max_files is not None:
        files = files[:max_files]
    print(f"\U0001f50d Encontrados {len(files)} archivos Markdown.")
    indexed_docs = 0
    indexed_chunks = 0
    new_chunk_data: list[tuple[int, np.ndarray]] = []

    with get_connection() as conn:
        for i, file_path in enumerate(files):
            if i % 10 == 0:
                print(f"\U0001f4d6 Procesando {i}/{len(files)}: {file_path.name}")
            doc = load_document(file_path)
            path_str = str(doc.path)

            existing = conn.execute(
                "SELECT id, file_hash FROM documents WHERE path = ?",
                (path_str,),
            ).fetchone()

            if existing and existing["file_hash"] == doc.file_hash:
                continue

            if existing:
                doc_id = existing["id"]
                conn.execute(
                    """UPDATE documents
                       SET title=?, file_hash=?, file_size_bytes=?,
                           modified_at=?, updated_at=datetime('now')
                       WHERE id=?""",
                    (doc.title, doc.file_hash, doc.file_size_bytes, doc.modified_at, doc_id),
                )
                conn.execute("DELETE FROM chunks WHERE document_id=?", (doc_id,))
            else:
                cursor = conn.execute(
                    """INSERT INTO documents (path, title, file_hash, file_size_bytes, modified_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (path_str, doc.title, doc.file_hash, doc.file_size_bytes, doc.modified_at),
                )
                doc_id = cursor.lastrowid

            for chunk in doc.chunks:
                embed_text = f"{chunk.heading}\n\n{chunk.content}"
                embedding = client.embed(embed_text)
                blob = embedding_to_blob(embedding)
                meta_json = json.dumps(chunk.meta or {}, ensure_ascii=False)
                cursor = conn.execute(
                    """INSERT INTO chunks
                       (document_id, chunk_index, heading, content, token_estimate, embedding)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (doc_id, chunk.chunk_index, chunk.heading, chunk.content, chunk.token_estimate, blob),
                )
                indexed_chunks += 1
                emb_arr = np.frombuffer(blob, dtype=np.float32)
                new_chunk_data.append((cursor.lastrowid, emb_arr))

            indexed_docs += 1
            conn.commit()

    _build_faiss_index(new_chunk_data=new_chunk_data)
    return {"documents": indexed_docs, "chunks": indexed_chunks}


def ingest_single_file(file_path: str) -> dict[str, int]:
    return ingest_paths([file_path])


# ── FAISS index management ────────────────────────────────────
_faiss_cache: tuple | None = None


def _invalidate_faiss_cache() -> None:
    global _faiss_cache
    _faiss_cache = None


def _get_faiss_index() -> tuple:
    global _faiss_cache
    if _faiss_cache is not None:
        return _faiss_cache
    idx, ids = load_faiss_index()
    if idx is not None:
        _faiss_cache = (idx, ids)
    return idx, ids


def _build_faiss_index(
    new_chunk_data: list[tuple[int, np.ndarray]] | None = None,
) -> None:
    try:
        import faiss
    except ImportError:
        return

    idx_path = Path(settings.faiss_index_path)
    ids_path = Path(settings.faiss_id_map_path)
    dim = settings.rag_vector_dim

    if new_chunk_data and idx_path.exists():
        try:
            index = faiss.read_index(str(idx_path))
            try:
                existing_ids = json.loads(ids_path.read_text(encoding="utf-8"))
            except Exception:
                existing_ids = []
            new_ids = np.array([cid for cid, _ in new_chunk_data], dtype=np.int64)
            new_vecs = np.array([vec for _, vec in new_chunk_data], dtype=np.float32)
            new_vecs = new_vecs.reshape(len(new_chunk_data), dim)
            index.add_with_ids(new_vecs, new_ids)
            existing_ids.extend(int(cid) for cid, _ in new_chunk_data)
            faiss.write_index(index, str(idx_path))
            ids_path.write_text(json.dumps(existing_ids), encoding="utf-8")
            _invalidate_faiss_cache()
            return
        except Exception:
            pass

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, embedding FROM chunks WHERE embedding IS NOT NULL"
        ).fetchall()

    if not rows:
        return

    vectors = np.zeros((len(rows), dim), dtype=np.float32)
    ids = np.zeros(len(rows), dtype=np.int64)

    for i, row in enumerate(rows):
        emb = np.frombuffer(row["embedding"], dtype=np.float32)
        vectors[i] = emb
        ids[i] = row["id"]

    index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
    index.add_with_ids(vectors, ids)

    faiss.write_index(index, str(idx_path))
    ids_path.write_text(
        json.dumps([int(i) for i in ids]), encoding="utf-8"
    )
    _invalidate_faiss_cache()


def load_faiss_index() -> tuple:
    try:
        import faiss
    except ImportError:
        return None, None

    idx_path = Path(settings.faiss_index_path)
    if not idx_path.exists():
        return None, None

    index = faiss.read_index(str(idx_path))
    ids_path = Path(settings.faiss_id_map_path)
    if ids_path.exists():
        try:
            chunk_ids = json.loads(ids_path.read_text(encoding="utf-8"))
            return index, chunk_ids
        except Exception:
            pass

    return index, None
