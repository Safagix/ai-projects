"""Ollama HTTP client with multi-model support, streaming, and connection pooling."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Generator

import httpx
from cachetools import TTLCache
from httpx import HTTPTransport, Limits, Timeout

from local_rag.config import settings

_EMBED_CACHE: TTLCache = TTLCache(maxsize=512, ttl=300)

_MAX_CONNECTIONS = 20
_MAX_KEEPALIVE = 10
_TIMEOUT = Timeout(60.0, connect=10.0, read=300.0, write=60.0, pool=10.0)
_LIMITS = Limits(max_connections=_MAX_CONNECTIONS, max_keepalive_connections=_MAX_KEEPALIVE)

_transport = HTTPTransport(retries=3)
_client: httpx.Client | None = None


def _embed_cache_key(text: str) -> str:
    return hashlib.sha256(f"{settings.ollama_embed_model}:{text}".encode()).hexdigest()


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=settings.ollama_base_url.rstrip("/"),
            timeout=_TIMEOUT,
            limits=_LIMITS,
            transport=_transport,
        )
    return _client


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        if base_url:
            self._base_url = base_url.rstrip("/")
            self._client = httpx.Client(
                base_url=self._base_url,
                timeout=_TIMEOUT,
                limits=_LIMITS,
                transport=_transport,
            )
        else:
            self._base_url = settings.ollama_base_url.rstrip("/")
            self._client = _get_client()

    # ── Embeddings ────────────────────────────────────────
    def embed(self, text: str | list[str]) -> list[float]:
        if isinstance(text, list):
            return self._embed_batch(text)
        return self._single_embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if len(texts) == 1:
            return [self._single_embed(texts[0])]

        results: list[list[float]] = []
        uncached_texts: list[tuple[int, str]] = []
        for i, t in enumerate(texts):
            key = _embed_cache_key(t)
            cached = _EMBED_CACHE.get(key)
            if cached is not None:
                results.append(cached)
            else:
                results.append([])
                uncached_texts.append((i, t))

        if not uncached_texts:
            return results

        batch = [t for _, t in uncached_texts]
        resp = self._client.post(
            "/api/embed",
            json={"model": settings.ollama_embed_model, "input": batch},
        )
        resp.raise_for_status()
        embeddings = resp.json().get("embeddings")
        if not isinstance(embeddings, list):
            raise RuntimeError("Ollama returned invalid batch embeddings.")

        for idx, (orig_idx, text) in enumerate(uncached_texts):
            emb = embeddings[idx]
            if not isinstance(emb, list) or not emb:
                raise RuntimeError("Ollama returned an invalid embedding.")
            result = [float(v) for v in emb]
            results[orig_idx] = result
            _EMBED_CACHE[_embed_cache_key(text)] = result

        return results

    def _single_embed(self, text: str) -> list[float]:
        key = _embed_cache_key(text)
        cached = _EMBED_CACHE.get(key)
        if cached is not None:
            return cached
        resp = self._client.post(
            "/api/embeddings",
            json={"model": settings.ollama_embed_model, "prompt": text},
        )
        resp.raise_for_status()
        embedding = resp.json().get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Ollama returned an invalid embedding.")
        result = [float(v) for v in embedding]
        _EMBED_CACHE[key] = result
        return result

    def _embed_batch(self, texts: list[str]) -> list[float]:
        return self._single_embed(texts[0])

    # ── Chat (blocking) ───────────────────────────────────
    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> str:
        resp = self._client.post(
            "/api/chat",
            json={
                "model": model or settings.model_fast,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
        )
        resp.raise_for_status()
        return str(resp.json()["message"]["content"]).strip()

    # ── Chat (streaming via generator) ────────────────────
    def chat_stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> Generator[str, None, None]:
        with self._client.stream(
            "POST",
            "/api/chat",
            json={
                "model": model or settings.model_fast,
                "messages": messages,
                "stream": True,
                "options": {"temperature": temperature},
            },
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    # ── List available models ─────────────────────────────
    def list_models(self) -> list[dict[str, Any]]:
        resp = self._client.get("/api/tags")
        resp.raise_for_status()
        return resp.json().get("models", [])

    # ── Health check ──────────────────────────────────────
    def health(self) -> dict[str, Any]:
        try:
            resp = self._client.get("/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"status": "ok", "models": models}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def close(self) -> None:
        if self._client is not _get_client():
            self._client.close()


_ollama: OllamaClient | None = None


def get_ollama():
    global _ollama
    if _ollama is None:
        if settings.optillm_enabled:
            from local_rag.optillm_client import OptillmClient
            _ollama = OptillmClient()
        else:
            _ollama = OllamaClient()
    return _ollama
