"""LLM Router — Uses the fastest model to classify queries and pick the best model."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from local_rag.config import settings
from local_rag.ollama_client import get_ollama

ROUTER_PROMPT = """Classify the user message into ONE category. Reply with ONLY the category word, nothing else.

Categories:
- SEARCH: User wants to find or ask about information in their knowledge base
- CODE: User wants code, JSON, technical data structures, or programming help
- ANALYZE: User wants deep analysis, reasoning, comparison, or strategic thinking
- WRITE: User wants to save, add, or store new information in their knowledge base
- CHAT: General conversation, greetings, or meta-questions about the system

Reply with exactly one word: SEARCH, CODE, ANALYZE, WRITE, or CHAT"""

CATEGORY_TO_MODEL = {
    "SEARCH": "fast",
    "CODE": "coder",
    "ANALYZE": "thinker",
    "WRITE": "fast",
    "CHAT": "fast",
}

CATEGORY_TO_TEMP = {
    "SEARCH": 0.3,
    "CODE": 0.2,
    "ANALYZE": 0.3,
    "WRITE": 0.5,
    "CHAT": 0.7,
}

SEARCH_MARKERS = (
    "busca",
    "buscar",
    "buscame",
    "base de datos",
    "biblioteca",
    "knowledge base",
    "obsidian",
    "eira's library",
    "segun ",
    "según ",
    "fuente",
    "fuentes",
    "que sabes",
    "qué sabes",
    "explica",
    "explicame",
    "explícame",
    "resume",
    "resumen",
)

SEARCH_DOMAIN_TERMS = (
    "template",
    "templates",
    "workflow",
    "workflows",
    "n8n",
    "whatsapp",
    "telegram",
    "google sheets",
    "gmail",
    "slack",
    "webhook",
    "automatizacion",
    "automatización",
    "integracion",
    "integración",
)

WRITE_MARKERS = (
    "guarda",
    "guardar",
    "anota",
    "agrega",
    "añade",
    "crear nota",
    "crea una nota",
    "guarda en obsidian",
    "guardar en obsidian",
)

QUESTION_PATTERNS = (
    "que es", "qué es", "que son", "qué son", "como ", "cómo ",
    "donde ", "dónde ", "cuando ", "cuándo ", "cual ", "cuál ",
    "cuales ", "cuáles ", "quien ", "quién ", "por que", "por qué",
    "para que", "para qué", "cuanto ", "cuánto ",
    "what ", "how ", "where ", "when ", "why ", "who ", "which ",
    "explícame", "explicame", "explica", "explique",
    "dime", "decime", "dame", "muestrame", "muéstrame",
    "resume", "resumime", "listame", "encontrame",
    "buscame", "busca", "buscar",
)

CODE_PATTERNS = (
    "codigo", "código", "script", "programa", "función", "funcion",
    "clase", "api", "json", "yaml", "docker", "python", "javascript",
    "typescript", "react", "vue", "svelte", "html", "css", "sql",
    "escribe un", "genera un", "generame", "generá",
)

HEURISTIC_SEARCH = "SEARCH"
HEURISTIC_CODE = "CODE"
HEURISTIC_WRITE = "WRITE"
HEURISTIC_UNCERTAIN = None


@dataclass
class RoutingDecision:
    category: str
    model_key: str
    model_name: str
    temperature: float
    needs_rag: bool
    needs_write: bool


def _normalize(text: str) -> str:
    ascii_text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in ascii_text if unicodedata.category(ch) != "Mn").strip()


def _strip_write_prefix(text: str) -> str:
    normalized = _normalize(text)
    prefix = "[guardar en obsidian]"
    if normalized.startswith(prefix):
        return text[text.lower().find("]") + 1:].strip()
    return text.strip()


def _looks_like_search(text: str) -> bool:
    normalized = _normalize(text)
    if any(marker in normalized for marker in SEARCH_MARKERS):
        return True

    domain_hits = sum(1 for term in SEARCH_DOMAIN_TERMS if term in normalized)
    return domain_hits >= 2


def _looks_like_write(text: str) -> bool:
    normalized = _normalize(text)
    if normalized.startswith("[guardar en obsidian]"):
        body = _strip_write_prefix(text)
        return bool(body) and not _looks_like_search(body)
    return False


def route(user_message: str) -> RoutingDecision:
    """Classify the user's message and pick the best model."""
    client = get_ollama()
    normalized = _normalize(user_message)
    clean_message = _strip_write_prefix(user_message)

    # Heuristic short-circuit: avoid LLM router call when confidence is high
    heuristic_category = _heuristic_classify(normalized, clean_message)

    if heuristic_category is not None:
        category = heuristic_category
    else:
        try:
            raw = client.chat(
                [
                    {"role": "system", "content": ROUTER_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                model=settings.router_model,
                temperature=0.1,
            )
            category = "SEARCH"
            for word in raw.upper().split():
                clean = word.strip(".,;:!?\"'`*")
                if clean in CATEGORY_TO_MODEL:
                    category = clean
                    break
        except Exception:
            category = "SEARCH"

    # Secure override: NEVER save notes from the chat router unless explicitly prefixed!
    has_write_prefix = user_message.lower().startswith("[guardar en obsidian]")
    if category == "WRITE" and not has_write_prefix:
        category = "SEARCH"

    model_key = CATEGORY_TO_MODEL[category]
    return RoutingDecision(
        category=category,
        model_key=model_key,
        model_name=settings.model_map[model_key],
        temperature=CATEGORY_TO_TEMP[category],
        needs_rag=category in ("SEARCH", "ANALYZE", "CODE"),
        needs_write=category == "WRITE" and has_write_prefix,
    )


def _heuristic_classify(normalized: str, clean_message: str) -> str | None:
    if _looks_like_write(normalized):
        return HEURISTIC_WRITE

    if any(marker in normalized for marker in QUESTION_PATTERNS) or normalized.endswith("?"):
        if any(marker in normalized for marker in CODE_PATTERNS):
            return HEURISTIC_CODE
        return HEURISTIC_SEARCH

    if _looks_like_search(normalized) or any(marker in normalized for marker in (".md", "_")):
        return HEURISTIC_SEARCH

    if any(marker in normalized for marker in CODE_PATTERNS):
        return HEURISTIC_CODE

    return HEURISTIC_UNCERTAIN
