"""Chat engine — Orchestrates routing, RAG retrieval, and response generation."""

from __future__ import annotations

import asyncio
import fnmatch
import json
import subprocess
import unicodedata
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Any, Generator

from cachetools import TTLCache

from local_rag.config import settings
from local_rag.ollama_client import get_ollama
from local_rag.retrieval import search
from local_rag.router import RoutingDecision, route
from local_rag.writer import write_note

SYSTEM_PROMPT = (
    "Eres **Eira Brain**, el asistente personal de conocimiento del usuario. "
    "Tu base de datos es su biblioteca personal (Eira's Library + Obsidian Vault). "
    "Reglas:\n"
    "1. Responde SOLO basándote en el contexto proporcionado.\n"
    "2. Si la respuesta no está en el contexto, dilo claramente.\n"
    "3. Cita fuentes con [Fuente N].\n"
    "4. Responde en el idioma en que te preguntan.\n"
    "5. Sé conciso y útil."
)


class ChatSession:
    def __init__(self, max_history: int = 10):
        self.history: list[dict[str, str]] = []
        self.max_history = max_history
        self._lock = asyncio.Lock()

    def add_user(self, content: str) -> None:
        self.history.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str) -> None:
        self.history.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self) -> None:
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def get_messages(self, system: str, context: str | None = None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        if context:
            messages.append({
                "role": "system",
                "content": f"Contexto de la base de conocimiento:\n\n{context}",
            })
        messages.extend(self.history)
        return messages


_sessions: TTLCache = TTLCache(maxsize=128, ttl=3600)
CURRENT_LANG = "es"
VOICE_ID = "es-MX-DaliaNeural"

FOLLOWUP_MARKERS = (
    "explicame mas", "explica mas", "amplia", "ampliame",
    "dame mas", "mas detalle", "mas detalles", "continua", "seguime",
)


def get_session(session_id: str) -> ChatSession:
    session = _sessions.get(session_id)
    if session is None:
        session = ChatSession()
        _sessions[session_id] = session
    return session


def _normalize(text: str) -> str:
    ascii_text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in ascii_text if unicodedata.category(ch) != "Mn").strip()


def _strip_write_prefix(text: str) -> str:
    normalized = _normalize(text)
    prefix = "[guardar en obsidian]"
    if normalized.startswith(prefix):
        return text[text.lower().find("]") + 1:].strip()
    return text.strip()


def _last_user_message(session: ChatSession) -> str | None:
    for item in reversed(session.history):
        if item.get("role") == "user" and item.get("content"):
            return item["content"]
    return None


def _is_followup(user_message: str) -> bool:
    normalized = _normalize(user_message)
    return any(marker in normalized for marker in FOLLOWUP_MARKERS)


def _compact_snippet(text: str, max_chars: int = 420) -> str:
    if "| Workflow |" in text and "| --- |" in text:
        rows = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line.startswith("|") or line.startswith("| ---") or " Workflow " in line:
                continue
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if len(cells) < 6:
                continue
            workflow, _category, integrations, triggers, nodes, source = cells[:6]
            rows.append(f"- {workflow}: {triggers}. Source: `{source}`. Nodes: {nodes}.")
            if len(rows) >= 6:
                break
        if rows:
            return "\n".join(rows)

    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 1].rstrip() + "..."


def _match_rule(match: dict[str, Any], rule: dict) -> bool:
    field = rule.get("field", "")
    op = rule.get("op", "contains")
    value = rule.get("value", "").lower()
    match_value = str(match.get(field, "")).lower()

    if op == "contains":
        return value in match_value
    if op == "starts_with":
        if not match_value.startswith(value):
            return False
        extra = rule.get("extra", "")
        if extra:
            return extra.lower() in match_value
        return True
    if op == "ends_with":
        return match_value.endswith(value.rstrip("/").rstrip("\\"))
    if op == "eq":
        if rule.get("require_content_start"):
            return match_value == value and str(match.get("content", "")).strip().startswith(
                rule["require_content_start"]
            )
        return match_value == value
    if op == "eq_compact":
        return " ".join(match_value.split()) == value
    return False


def _is_low_value_match(match: dict[str, Any]) -> bool:
    content = str(match.get("content") or "").strip()
    if not content:
        return True
    for rule in settings.low_value_patterns:
        if _match_rule(match, rule):
            return True
    return False


def _search_specificity(match: dict[str, Any]) -> tuple[int, float]:
    keyword_score = float(match.get("keyword_score") or 0)
    score = 0
    path = str(match.get("path") or "").lower()
    heading = str(match.get("heading") or "").lower()
    content = str(match.get("content") or "").lower()

    for rule in settings.boost_rules:
        if _match_rule({"path": path, "heading": heading, "content": content}, rule):
            score += rule.get("boost", 0)

    return score, keyword_score


def _format_search_answer(matches: list[dict[str, Any]]) -> str:
    matches = [m for m in matches if not _is_low_value_match(m)]
    matches = sorted(matches, key=_search_specificity, reverse=True)
    relevant = [
        m for m in matches
        if float(m.get("keyword_score") or 0) > 0 or float(m.get("semantic_score") or 0) >= 0.69
    ][:4]
    if not relevant:
        relevant = matches[:3]

    lines = ["Encontré esto en tu base de conocimiento:"]
    for idx, match in enumerate(relevant, start=1):
        heading = match.get("heading") or match.get("doc_title") or "Documento"
        lines.append(f"\n[Fuente {idx}] **{heading}**")
        lines.append(_compact_snippet(str(match.get("content") or "")))

    return "\n".join(lines)


def process_message(
    user_message: str,
    session_id: str = "default",
) -> Generator[str, None, None]:
    try:
        global CURRENT_LANG, VOICE_ID
        session = get_session(session_id)
        client = get_ollama()

        # ── Step 0: Intercept Language Commands ────────────
        text_lower = user_message.lower()
        if "switch to english" in text_lower or "cambiate a ingles" in text_lower:
            CURRENT_LANG = "en"
            VOICE_ID = "en-US-JennyNeural"
            resp = "Acknowledged. Switching to English mode."
            yield _sse_event("chunk", {"text": resp})
            yield _sse_event("audio", {"url": _generate_tts(resp)})
            yield _sse_event("done", {"model": "system", "category": "COMMAND", "citations": []})
            return

        elif "switch to japanese" in text_lower or "cambia a japones" in text_lower or "cambiate a japones" in text_lower:
            CURRENT_LANG = "ja"
            VOICE_ID = "ja-JP-NanamiNeural"
            resp = "\u627f\u77e5\u3044\u305f\u3057\u307e\u3057\u305f\u3002\u65e5\u672c\u8a9e\u30e2\u30fc\u30c9\u306b\u5207\u308a\u66ff\u3048\u307e\u3059\u3002"
            yield _sse_event("chunk", {"text": resp})
            yield _sse_event("audio", {"url": _generate_tts(resp)})
            yield _sse_event("done", {"model": "system", "category": "COMMAND", "citations": []})
            return

        elif "switch to spanish" in text_lower or "cambia a espa\u00f1ol" in text_lower:
            CURRENT_LANG = "es"
            VOICE_ID = "es-MX-DaliaNeural"
            resp = "Entendido. Volviendo al espa\u00f1ol."
            yield _sse_event("chunk", {"text": resp})
            yield _sse_event("audio", {"url": _generate_tts(resp)})
            yield _sse_event("done", {"model": "system", "category": "COMMAND", "citations": []})
            return

        # ── Step 1: Route ──────────────────────────────────
        clean_user_message = _strip_write_prefix(user_message)
        decision = route(user_message)
        effective_query = clean_user_message

        if decision.category == "CHAT" and _is_followup(clean_user_message):
            previous_user_message = _last_user_message(session)
            if previous_user_message:
                decision = replace(
                    decision,
                    category="SEARCH",
                    model_key="fast",
                    model_name=settings.model_fast,
                    temperature=0.3,
                    needs_rag=True,
                    needs_write=False,
                )
                effective_query = f"{previous_user_message}\n{clean_user_message}"

        yield _sse_event("routing", {
            "category": decision.category,
            "model": decision.model_name,
            "model_key": decision.model_key,
        })

        # ── Step 2: Handle WRITE intent ────────────────────
        if decision.needs_write:
            yield _sse_event("status", {"message": "Guardando nota en Obsidian..."})
            clean_message = clean_user_message
            result = write_note(clean_message)
            response_text = (
                f"\u2705 **Nota guardada en Obsidian**\n\n"
                f"\U0001f4c1 **Archivo:** `{result['filename']}`\n"
                f"\U0001f4c2 **Carpeta:** `{result['folder']}`\n"
            )
            if result.get("tags"):
                response_text += f"\U0001f3f7\ufe0f **Tags:** {', '.join(result['tags'])}\n"

            session.add_user(clean_message)
            session.add_assistant(response_text)

            yield _sse_event("chunk", {"text": response_text})
            yield _sse_event("done", {
                "model": decision.model_name,
                "category": decision.category,
                "citations": [],
            })
            return

        # ── Step 3: RAG retrieval (if needed) ──────────────
        context_text = ""
        citations: list[dict[str, Any]] = []

        if decision.needs_rag:
            yield _sse_event("status", {"message": "Buscando en la base de conocimiento..."})
            search_limit = max(settings.rag_context_limit, 12) if decision.category == "SEARCH" else settings.rag_context_limit
            matches = search(effective_query, limit=search_limit)
            matches = [m for m in matches if not _is_low_value_match(m)]
            if decision.category == "SEARCH":
                matches = sorted(matches, key=_search_specificity, reverse=True)[: settings.rag_context_limit]

            context_parts: list[str] = []
            for idx, match in enumerate(matches, start=1):
                context_parts.append(
                    "\n".join([
                        f"[Fuente {idx}]",
                        f"Archivo: {match['path']}",
                        f"Secci\u00f3n: {match['heading'] or 'Documento'}",
                        match["content"],
                    ])
                )
                citations.append({
                    "path": match["path"],
                    "heading": match["heading"],
                    "score": round(float(match["fused_score"]), 4),
                })

            context_text = "\n\n".join(context_parts)

            if not matches:
                response_text = (
                    "No encontr\u00e9 contexto relevante en la base de conocimiento para esa consulta. "
                    "Re-index\u00e1 la base si sab\u00e9s que esa informaci\u00f3n existe."
                )
                session.add_user(clean_user_message)
                session.add_assistant(response_text)
                yield _sse_event("chunk", {"text": response_text})
                yield _sse_event("done", {
                    "model": decision.model_name,
                    "category": decision.category,
                    "citations": [],
                })
                return

            if decision.category == "SEARCH":
                response_text = _format_search_answer(matches)
                session.add_user(clean_user_message)
                session.add_assistant(response_text)
                yield _sse_event("chunk", {"text": response_text})
                yield _sse_event("done", {
                    "model": decision.model_name,
                    "category": decision.category,
                    "citations": citations,
                })
                return

        # ── Step 4: Generate response (streaming) ─────────
        session.add_user(clean_user_message)

        lang_instruction = ""
        if CURRENT_LANG == "en":
            lang_instruction = " Always answer in English."
        elif CURRENT_LANG == "ja":
            lang_instruction = " \u5e38\u306b\u65e5\u672c\u8a9e\u3067\u7b54\u3048\u3066\u304f\u3060\u3055\u3044\u3002"

        messages = session.get_messages(SYSTEM_PROMPT + lang_instruction, context_text or None)

        yield _sse_event("status", {"message": f"Generando respuesta con {decision.model_name}..."})

        full_response = []
        for token in client.chat_stream(
            messages,
            model=decision.model_name,
            temperature=decision.temperature,
            model_key=decision.model_key,
        ):
            full_response.append(token)
            yield _sse_event("chunk", {"text": token})

        response_text = "".join(full_response).strip()
        if not response_text:
            raise RuntimeError("El modelo local no devolvi\u00f3 contenido.")
        session.add_assistant(response_text)

        audio_url = _generate_tts(response_text) if settings.rag_enable_tts else None
        if audio_url:
            yield _sse_event("audio", {"url": audio_url})

        yield _sse_event("done", {
            "model": decision.model_name,
            "category": decision.category,
            "citations": citations,
        })
    except Exception as exc:
        yield _sse_event("error", {"message": str(exc)})
        yield _sse_event("done", {"model": "", "category": "ERROR", "citations": []})


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _generate_tts(text: str) -> str | None:
    try:
        static_dir = Path(__file__).resolve().parents[2] / "static" / "audio"
        static_dir.mkdir(parents=True, exist_ok=True)

        clean_text = text.replace("**", "").replace("*", "")
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        filepath = static_dir / filename

        cmd = ["edge-tts", "--voice", VOICE_ID, "--text", clean_text, "--write-media", str(filepath)]
        subprocess.run(cmd, check=True, capture_output=True)

        return f"/static/audio/{filename}"
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None
