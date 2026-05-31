"""FastAPI application — Chat API + static file serving."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from local_rag.chat import process_message
from local_rag.db import init_db
from local_rag.indexer import ingest_paths
from local_rag.ollama_client import get_ollama
from local_rag.retrieval import answer, search
from local_rag.uiux_collector import collect_component
from local_rag.writer import write_note

limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])

app = FastAPI(title="Eira Brain Chat", version="0.2.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

_TTS_MAX_AGE = 600  # 10 minutes


# ── Request models ────────────────────────────────────────
class ChatBody(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(default="default")


class WriteBody(BaseModel):
    content: str = Field(min_length=3)
    title: str | None = None


class AskBody(BaseModel):
    question: str = Field(min_length=3)


class SearchBody(BaseModel):
    question: str = Field(min_length=3)
    limit: int = Field(default=8, ge=1, le=20)


class UIUXCollectBody(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default="")
    code: str = Field(min_length=1)
    force: bool = Field(default=False)


class IngestBody(BaseModel):
    paths: list[str] = Field(default_factory=list)


# ── Chat endpoint (SSE streaming) ────────────────────────
@app.post("/api/chat")
@limiter.limit("10/minute")
def chat_endpoint(body: ChatBody, request: Request):
    def event_stream():
        for event in process_message(body.message, body.session_id):
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Write to Obsidian ────────────────────────────────────
@app.post("/api/write")
@limiter.limit("10/minute")
def write_endpoint(body: WriteBody, request: Request) -> dict[str, Any]:
    return write_note(body.content, title=body.title)


# ── UI/UX Collector ─────────────────────────────────────
@app.post("/api/uiux-collect")
@limiter.limit("10/minute")
def uiux_collect_endpoint(body: UIUXCollectBody, request: Request) -> dict[str, Any]:
    return collect_component(
        body.name, body.description, body.code, force=body.force
    )


# ── Legacy RAG endpoints ─────────────────────────────────
@app.post("/api/ask")
@limiter.limit("10/minute")
def ask_endpoint(body: AskBody, request: Request) -> dict[str, Any]:
    return answer(body.question)


@app.post("/api/search")
@limiter.limit("20/minute")
def search_endpoint(body: SearchBody, request: Request) -> dict[str, Any]:
    return {"matches": search(body.question, limit=body.limit)}


@app.post("/api/ingest")
@limiter.limit("2/minute")
def ingest_endpoint(body: IngestBody, request: Request) -> dict[str, int]:
    return ingest_paths(body.paths or None)


@app.post("/api/init-db")
@limiter.limit("2/minute")
def init_db_endpoint(request: Request) -> dict[str, str]:
    init_db()
    return {"status": "ok", "message": "Database initialized."}


# ── System info ──────────────────────────────────────────
@app.get("/api/health")
def health() -> dict[str, Any]:
    client = get_ollama()
    return {"status": "ok", "ollama": client.health()}


@app.get("/api/models")
def list_models() -> dict[str, Any]:
    client = get_ollama()
    return {"models": client.list_models()}


# ── Serve static frontend ───────────────────────────────
@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.on_event("startup")
def _cleanup_old_tts_files():
    """Delete TTS audio files older than TTS_MAX_AGE seconds."""
    audio_dir = STATIC_DIR / "audio"
    if not audio_dir.exists():
        return
    now = time.time()
    for f in audio_dir.glob("tts_*.mp3"):
        try:
            if now - f.stat().st_mtime > _TTS_MAX_AGE:
                f.unlink()
        except Exception:
            pass


# Mount static files AFTER explicit routes
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
