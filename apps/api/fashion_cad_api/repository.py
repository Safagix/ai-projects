from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import settings
from .schemas import CreateDesignRequest, OperationRequest


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class GpuBusyError(RuntimeError):
    pass


class Repository:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or settings.database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS designs (
                    id TEXT PRIMARY KEY,
                    document_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    design_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    operation_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(design_id, revision)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS rag_documents USING fts5(
                    title, content, source, tokenize='unicode61'
                );
                CREATE TABLE IF NOT EXISTS rag_document_metadata (
                    rag_row_id INTEGER PRIMARY KEY,
                    source_page INTEGER,
                    chunk_number INTEGER,
                    FOREIGN KEY(rag_row_id) REFERENCES rag_documents(rowid)
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gpu_exclusive INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    total INTEGER,
                    message TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cloud_consents (
                    id TEXT PRIMARY KEY,
                    design_id TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    estimated_cost_usd REAL NOT NULL,
                    approved INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS operator_audit (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    window_name TEXT,
                    outcome TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS operator_audit_session_created
                    ON operator_audit(session_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS semantic_index_state (
                    index_name TEXT PRIMARY KEY,
                    table_name TEXT,
                    model_id TEXT NOT NULL,
                    source_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._ensure_column(connection, "jobs", "progress", "INTEGER NOT NULL DEFAULT 0")
            self._ensure_column(connection, "jobs", "total", "INTEGER")
            self._ensure_column(connection, "jobs", "message", "TEXT")
            self._ensure_column(connection, "jobs", "error", "TEXT")

    @staticmethod
    def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def create_design(self, payload: CreateDesignRequest) -> dict[str, Any]:
        now = utc_now()
        design_id = str(uuid.uuid4())
        document = {
            "id": design_id,
            "name": payload.name,
            "product_type": payload.product_type,
            "mode": payload.mode,
            "description": payload.description,
            "measurements_mm": payload.measurements_mm.model_dump(),
            "materials": payload.materials,
            "components": payload.components,
            "revision": 1,
            "approval_state": "draft",
            "confidence": "manual",
            "cloud_consent": payload.cloud_consent,
            "created_at": now,
            "updated_at": now,
        }
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO designs(id, document_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (design_id, json.dumps(document), now, now),
            )
            connection.execute(
                "INSERT INTO revisions(design_id, revision, operation_json, created_at) VALUES (?, ?, ?, ?)",
                (design_id, 1, json.dumps({"kind": "create"}), now),
            )
        return document

    def get_design(self, design_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT document_json FROM designs WHERE id = ?", (design_id,)).fetchone()
        return json.loads(row["document_json"]) if row else None

    def list_designs(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT document_json FROM designs ORDER BY updated_at DESC").fetchall()
        return [json.loads(row["document_json"]) for row in rows]

    def apply_operation(self, design_id: str, operation: OperationRequest) -> dict[str, Any] | None:
        document = self.get_design(design_id)
        if document is None:
            return None
        if operation.kind == "add_component":
            component = str(operation.value).strip()
            if component and component not in document["components"]:
                document["components"].append(component)
        elif operation.kind == "remove_component":
            component = str(operation.value)
            document["components"] = [item for item in document["components"] if item != component]
        elif operation.kind == "set_materials":
            document["materials"] = [str(item).strip() for item in operation.value if str(item).strip()]
        elif operation.kind == "set_description":
            document["description"] = str(operation.value)
        elif operation.kind == "set_mode":
            mode = str(operation.value)
            if mode not in {"local_private", "hybrid", "cloud_creative"}:
                raise ValueError("Modo no permitido")
            document["mode"] = mode
        elif operation.kind == "set_measurement":
            if not isinstance(operation.value, str) or ":" not in operation.value:
                raise ValueError("Usar formato nombre:milimetros, por ejemplo laptop_width_mm:355")
            name, raw_value = operation.value.split(":", 1)
            if name not in document["measurements_mm"]:
                raise ValueError("Medida no permitida")
            document["measurements_mm"][name] = float(raw_value)
        document["revision"] += 1
        document["confidence"] = "local_assisted"
        document["updated_at"] = utc_now()
        with self.connect() as connection:
            connection.execute(
                "UPDATE designs SET document_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(document), document["updated_at"], design_id),
            )
            connection.execute(
                "INSERT INTO revisions(design_id, revision, operation_json, created_at) VALUES (?, ?, ?, ?)",
                (design_id, document["revision"], operation.model_dump_json(), document["updated_at"]),
            )
        return document

    def add_rag_document(
        self, title: str, content: str, source: str, *, source_page: int | None = None, chunk_number: int | None = None
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO rag_documents(title, content, source) VALUES (?, ?, ?)",
                (title, content, source),
            )
            row_id = int(cursor.lastrowid)
            connection.execute(
                "INSERT OR REPLACE INTO rag_document_metadata(rag_row_id, source_page, chunk_number) VALUES (?, ?, ?)",
                (row_id, source_page, chunk_number),
            )
        return row_id

    def list_rag_documents(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT rag_documents.rowid AS id, title, content, source, source_page, chunk_number "
                "FROM rag_documents LEFT JOIN rag_document_metadata ON rag_row_id = rag_documents.rowid ORDER BY rag_documents.rowid"
            ).fetchall()
        return [dict(row) for row in rows]
    def search_rag(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT rag_documents.title, rag_documents.source, source_page, chunk_number, "
                "snippet(rag_documents, 1, '[', ']', '…', 18) AS excerpt, bm25(rag_documents) AS score "
                "FROM rag_documents LEFT JOIN rag_document_metadata ON rag_row_id = rag_documents.rowid "
                "WHERE rag_documents MATCH ? ORDER BY score LIMIT ?",
                (query, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_job(self, kind: str, payload: dict[str, Any], gpu_exclusive: bool) -> dict[str, Any]:
        now = utc_now()
        job_id = str(uuid.uuid4())
        with self.connect() as connection:
            if gpu_exclusive:
                active = connection.execute(
                    "SELECT id FROM jobs WHERE gpu_exclusive = 1 AND status IN ('queued', 'running') LIMIT 1"
                ).fetchone()
                if active:
                    raise GpuBusyError(f"GPU ocupada por trabajo {active['id']}")
            if kind == "embedding_index":
                active = connection.execute(
                    "SELECT id FROM jobs WHERE kind = 'embedding_index' AND status IN ('queued', 'running') LIMIT 1"
                ).fetchone()
                if active:
                    raise GpuBusyError(f"La indexación semántica está ocupada por trabajo {active['id']}")
            connection.execute(
                "INSERT INTO jobs(id, kind, status, gpu_exclusive, payload_json, progress, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (job_id, kind, "queued", int(gpu_exclusive), json.dumps(payload), 0, now, now),
            )
        return self.get_job(job_id) or {}

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "kind": row["kind"],
            "status": row["status"],
            "gpu_exclusive": bool(row["gpu_exclusive"]),
            "payload": json.loads(row["payload_json"]),
            "progress": int(row["progress"] or 0),
            "total": row["total"],
            "message": row["message"],
            "error": row["error"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def mark_job_running(self, job_id: str, *, total: int | None = None, message: str | None = None) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE jobs SET status = 'running', total = ?, message = ?, updated_at = ? WHERE id = ? AND status = 'queued'",
                (total, message, utc_now(), job_id),
            )
        return cursor.rowcount == 1

    def update_job_progress(self, job_id: str, progress: int, total: int, message: str | None = None) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE jobs SET progress = ?, total = ?, message = ?, updated_at = ? WHERE id = ? AND status = 'running'",
                (progress, total, message, utc_now(), job_id),
            )

    def complete_job(self, job_id: str, *, message: str | None = None) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE jobs SET status = 'completed', message = ?, error = NULL, updated_at = ? WHERE id = ? AND status = 'running'",
                (message, utc_now(), job_id),
            )

    def fail_job(self, job_id: str, error: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE jobs SET status = 'failed', error = ?, updated_at = ? WHERE id = ? AND status = 'running'",
                (error[:500], utc_now(), job_id),
            )

    def cancel_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE jobs SET status = 'cancelled', message = 'Cancelado por el usuario.', updated_at = ? "
                "WHERE id = ? AND status IN ('queued', 'running')",
                (utc_now(), job_id),
            )
        return self.get_job(job_id) if cursor.rowcount else None

    def is_job_cancelled(self, job_id: str) -> bool:
        with self.connect() as connection:
            row = connection.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return bool(row and row["status"] == "cancelled")

    def get_semantic_index(self, index_name: str = "rag_bge_m3") -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM semantic_index_state WHERE index_name = ?", (index_name,)).fetchone()
        return dict(row) if row else None

    def activate_semantic_index(self, table_name: str | None, source_count: int, *, model_id: str = "bge-m3") -> str | None:
        previous = self.get_semantic_index()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO semantic_index_state(index_name, table_name, model_id, source_count, created_at) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(index_name) DO UPDATE SET table_name = excluded.table_name, model_id = excluded.model_id, "
                "source_count = excluded.source_count, created_at = excluded.created_at",
                ("rag_bge_m3", table_name, model_id, source_count, utc_now()),
            )
        return previous["table_name"] if previous else None
    def record_cloud_consent(
        self,
        design_id: str,
        asset_id: str,
        provider: str,
        purpose: str,
        estimated_cost_usd: float,
        approved: bool,
    ) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "design_id": design_id,
            "asset_id": asset_id,
            "provider": provider,
            "purpose": purpose,
            "estimated_cost_usd": estimated_cost_usd,
            "approved": approved,
            "created_at": utc_now(),
        }
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO cloud_consents(id, design_id, asset_id, provider, purpose, estimated_cost_usd, approved, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"], record["design_id"], record["asset_id"], record["provider"], record["purpose"],
                    record["estimated_cost_usd"], int(record["approved"]), record["created_at"],
                ),
            )
        return record

    def list_cloud_consents(self, design_id: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM cloud_consents WHERE design_id = ? ORDER BY created_at DESC", (design_id,)
            ).fetchall()
        return [
            {
                "id": row["id"], "design_id": row["design_id"], "asset_id": row["asset_id"],
                "provider": row["provider"], "purpose": row["purpose"],
                "estimated_cost_usd": row["estimated_cost_usd"], "approved": bool(row["approved"]), "created_at": row["created_at"],
            }
            for row in rows
        ]

    def record_operator_audit(
        self,
        session_id: str,
        action: str,
        outcome: str,
        *,
        window_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "action": action,
            "window_name": window_name,
            "outcome": outcome,
            "details": details or {},
            "created_at": utc_now(),
        }
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO operator_audit(id, session_id, action, window_name, outcome, details_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"], record["session_id"], record["action"], record["window_name"],
                    record["outcome"], json.dumps(record["details"], ensure_ascii=False), record["created_at"],
                ),
            )
        return record

    def list_operator_audit(self, session_id: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM operator_audit WHERE session_id = ? ORDER BY created_at ASC, id ASC", (session_id,)
            ).fetchall()
        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "action": row["action"],
                "window_name": row["window_name"],
                "outcome": row["outcome"],
                "details": json.loads(row["details_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
