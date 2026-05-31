"""OptiLLM proxy client — OpenAI-compatible chat with automatic fallback to Ollama."""

from __future__ import annotations

from typing import Any, Generator

from openai import OpenAI

from local_rag.config import settings
from local_rag.ollama_client import OllamaClient


def _build_optillm_model(model_name: str, model_key: str | None = None) -> str:
    approach = _approach_for_key(model_key)
    if approach == "auto":
        return f"auto-{model_name}"
    return f"{approach}-{model_name}"


def _approach_for_key(model_key: str | None) -> str:
    if model_key and model_key in settings.optillm_approach_map:
        return settings.optillm_approach_map[model_key]
    return settings.optillm_default_approach


class OptillmClient:
    def __init__(self) -> None:
        self._ollama = OllamaClient()
        self._openai = OpenAI(
            base_url=settings.optillm_base_url,
            api_key="no-key",
        )

    def _optillm_available(self) -> bool:
        try:
            self._openai.models.list()
            return True
        except Exception:
            return False

    def _chat_via_optillm(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> str:
        optillm_model = _build_optillm_model(
            model or settings.model_fast, model_key
        )
        resp = self._openai.chat.completions.create(
            model=optillm_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    def _chat_via_ollama(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
    ) -> str:
        return self._ollama.chat(messages, model=model, temperature=temperature)

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> str:
        try:
            return self._chat_via_optillm(
                messages, model=model, temperature=temperature, model_key=model_key
            )
        except Exception:
            return self._chat_via_ollama(
                messages, model=model, temperature=temperature
            )

    def _chat_stream_via_optillm(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> Generator[str, None, None]:
        optillm_model = _build_optillm_model(
            model or settings.model_fast, model_key
        )
        stream = self._openai.chat.completions.create(
            model=optillm_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ],
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        model_key: str | None = None,
    ) -> Generator[str, None, None]:
        try:
            yield from self._chat_stream_via_optillm(
                messages, model=model, temperature=temperature, model_key=model_key
            )
        except Exception:
            yield from self._ollama.chat_stream(
                messages, model=model, temperature=temperature
            )

    def embed(self, text: str | list[str]) -> list[float]:
        return self._ollama.embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._ollama.embed_batch(texts)

    def list_models(self) -> list[dict[str, Any]]:
        return self._ollama.list_models()

    def health(self) -> dict[str, Any]:
        return self._ollama.health()

    def close(self) -> None:
        self._ollama.close()
        self._openai.close()
