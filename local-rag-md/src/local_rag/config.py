from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)


def _split(value: str, sep: str = ";") -> list[str]:
    return [p.strip() for p in value.split(sep) if p.strip()]


def _resolve_config_file(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[2] / p
    return p


def _load_json_config(path: str) -> dict:
    p = _resolve_config_file(path)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _default_low_value_patterns() -> list[dict]:
    return [
        {"field": "content", "op": "starts_with", "value": "---", "extra": "source: eira brain chat"},
        {"field": "path", "op": "ends_with", "value": "\\07-ideas\\templates_de_n8n_para_whatsapp.md"},
        {"field": "heading", "op": "eq", "value": "document", "require_content_start": "---"},
        {"field": "content", "op": "eq_compact", "value": "templates de n8n para whatsapp"},
        {"field": "content", "op": "eq_compact", "value": "template de n8n para whatsapp"},
    ]


def _default_boost_rules() -> list[dict]:
    return [
        {"field": "path", "op": "contains", "value": "integrations/whatsapp.md", "boost": 10},
        {"field": "heading", "op": "contains", "value": "workflow catalog", "boost": 8},
        {"field": "heading", "op": "contains", "value": "whatsapp workflows", "boost": 6},
        {"field": "content", "op": "contains", "value": "whatsapp trigger", "boost": 4},
        {"field": "content", "op": "contains", "value": "workflows detected", "boost": 2},
    ]


@dataclass(frozen=True)
class Settings:
    # ── Ollama ────────────────────────────────────────────
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    model_fast: str = os.getenv("OLLAMA_MODEL_FAST", "llama3.2:1b")
    model_thinker: str = os.getenv("OLLAMA_MODEL_THINKER", "deepseek-r1:1.5b")
    model_coder: str = os.getenv("OLLAMA_MODEL_CODER", "qwen2.5-coder:1.5b")
    router_model: str = os.getenv("OLLAMA_ROUTER_MODEL", "llama3.2:1b")

    # ── OptiLLM proxy ─────────────────────────────────────
    optillm_enabled: bool = os.getenv("OPTILLM_ENABLED", "false").lower() == "true"
    optillm_base_url: str = os.getenv("OPTILLM_BASE_URL", "http://127.0.0.1:8001/v1")
    optillm_default_approach: str = os.getenv("OPTILLM_DEFAULT_APPROACH", "auto")
    optillm_fast_approach: str = os.getenv("OPTILLM_FAST_APPROACH", "re2")
    optillm_thinker_approach: str = os.getenv("OPTILLM_THINKER_APPROACH", "cot_reflection")
    optillm_coder_approach: str = os.getenv("OPTILLM_CODER_APPROACH", "bon")

    # ── RAG ───────────────────────────────────────────────
    rag_vector_dim: int = int(os.getenv("RAG_VECTOR_DIM", "768"))
    rag_context_limit: int = int(os.getenv("RAG_CONTEXT_LIMIT", "6"))
    rag_semantic_candidates: int = int(os.getenv("RAG_SEMANTIC_CANDIDATES", "24"))
    rag_keyword_candidates: int = int(os.getenv("RAG_KEYWORD_CANDIDATES", "24"))
    rag_rrf_k: int = int(os.getenv("RAG_RRF_K", "50"))
    rag_batch_size: int = int(os.getenv("RAG_BATCH_SIZE", "32"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    rag_chunk_max_chars: int = int(os.getenv("RAG_CHUNK_MAX_CHARS", "1800"))
    rag_query_expand: bool = os.getenv("RAG_QUERY_EXPAND", "true").lower() == "true"
    rag_enable_tts: bool = os.getenv("RAG_ENABLE_TTS", "false").lower() == "true"

    # ── Knowledge paths ───────────────────────────────────
    rag_knowledge_dirs: tuple[str, ...] = tuple(
        _split(os.getenv("RAG_KNOWLEDGE_DIRS", str(Path.cwd())))
    )
    rag_include_globs: tuple[str, ...] = tuple(
        _split(os.getenv("RAG_INCLUDE_GLOBS", "**/*.md"))
    )
    rag_exclude_globs: tuple[str, ...] = tuple(
        _split(os.getenv("RAG_EXCLUDE_GLOBS", ""))
    )

    # ── Config files (low-value patterns & boost rules) ──
    low_value_config_path: str = os.getenv(
        "RAG_LOW_VALUE_CONFIG", "config/low_value_patterns.json"
    )
    boost_rules_config_path: str = os.getenv(
        "RAG_BOOST_RULES_CONFIG", "config/boost_rules.json"
    )

    # ── Obsidian ──────────────────────────────────────────
    obsidian_vault_path: str = os.getenv(
        "OBSIDIAN_VAULT_PATH",
        r"%DIGITAL_LAB%\Obsidian_Vault\Obsidian Vault",
    )
    obsidian_inbox_folder: str = os.getenv("OBSIDIAN_INBOX_FOLDER", "07-Ideas")

    # ── UI/UX Collector ───────────────────────────────────
    obsidian_uiux_folder: str = os.getenv(
        "OBSIDIAN_UIUX_FOLDER",
        r"%DIGITAL_LAB%\UI_UX_Components",
    )
    uiux_catalog_path: str = os.getenv(
        "UIUX_CATALOG_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "uiux_catalog.json"),
    )

    # ── SQLite ────────────────────────────────────────────
    sqlite_db_path: str = os.getenv(
        "SQLITE_DB_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "brain.db"),
    )

    # ── FAISS ─────────────────────────────────────────────
    faiss_index_path: str = os.getenv(
        "FAISS_INDEX_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "faiss.index"),
    )
    faiss_id_map_path: str = os.getenv(
        "FAISS_ID_MAP_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "faiss_ids.json"),
    )

    # ── Derived helpers ───────────────────────────────────
    @property
    def obsidian_inbox_path(self) -> Path:
        return Path(self.obsidian_vault_path) / self.obsidian_inbox_folder

    @property
    def model_map(self) -> dict[str, str]:
        return {
            "fast": self.model_fast,
            "thinker": self.model_thinker,
            "coder": self.model_coder,
        }

    @property
    def optillm_approach_map(self) -> dict[str, str]:
        return {
            "fast": self.optillm_fast_approach,
            "thinker": self.optillm_thinker_approach,
            "coder": self.optillm_coder_approach,
        }

    @property
    def low_value_patterns(self) -> list[dict]:
        return _load_json_config(self.low_value_config_path) or _default_low_value_patterns()

    @property
    def boost_rules(self) -> list[dict]:
        return _load_json_config(self.boost_rules_config_path) or _default_boost_rules()


settings = Settings()
