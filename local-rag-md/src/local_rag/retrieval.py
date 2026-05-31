"""Hybrid retrieval: FAISS cosine similarity + SQLite FTS5 with RRF fusion."""

from __future__ import annotations

import re
from typing import Any

import numpy as np

from local_rag.config import settings
from local_rag.db import get_connection, init_db
from local_rag.indexer import _get_faiss_index
from local_rag.ollama_client import get_ollama

STOPWORDS = {
    "sobre", "para", "quiero", "busca", "buscar", "busques", "buscame",
    "base", "datos", "dame", "info", "informacion", "informaci\u00f3n",
    "explica", "explicame", "expl\u00edcame", "mas", "m\u00e1s",
    "del", "con", "los", "las", "una", "uno", "que", "por", "como",
    "esta", "este",
}

QUERY_EXPAND_PROMPT = (
    "Rewrite the following question into 2 alternative search-friendly keyword queries "
    "that would help find relevant notes in a personal knowledge base. "
    "Return ONLY the 2 queries, one per line, no numbering or prefixes.\n\n"
    "Question: {question}"
)


def _query_terms(question: str) -> list[str]:
    return [
        term.lower()
        for term in re.findall(r"[\w.-]{3,}", question, flags=re.UNICODE)
        if not term.isnumeric() and term.lower() not in STOPWORDS
    ]


def _normalize_vec(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def _expand_query(question: str) -> list[str]:
    if not settings.rag_query_expand:
        return [question]
    try:
        client = get_ollama()
        response = client.chat(
            [
                {"role": "system", "content": "You are a search query optimizer."},
                {"role": "user", "content": QUERY_EXPAND_PROMPT.format(question=question)},
            ],
            model=settings.model_fast,
            temperature=0.3,
        )
        variants = [q.strip() for q in response.strip().splitlines() if q.strip()]
        variants = variants[:2]
    except Exception:
        variants = []
    return [question] + variants


def _faiss_search(q_embedding: np.ndarray, k: int) -> dict[int, float]:
    index, chunk_ids = _get_faiss_index()
    if index is not None and index.ntotal > 0:
        q = q_embedding.reshape(1, -1).astype(np.float32)
        scores, indices = index.search(q, k)
        result: dict[int, float] = {}
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            if chunk_ids and idx < len(chunk_ids):
                chunk_id = chunk_ids[idx]
            else:
                chunk_id = int(idx)
            result[chunk_id] = float(score)
        return result
    return {}


def search(question: str, *, limit: int | None = None) -> list[dict[str, Any]]:
    init_db()
    client = get_ollama()
    match_limit = limit or settings.rag_context_limit

    # Query expansion
    queries = _expand_query(question)

    # Embed all expanded queries and average
    embeddings = []
    for q in queries:
        emb = np.array(client.embed(q), dtype=np.float32)
        embeddings.append(_normalize_vec(emb))
    q_embedding = np.mean(embeddings, axis=0)
    q_embedding = _normalize_vec(q_embedding)

    with get_connection() as conn:
        # ── Semantic search (FAISS) ───────────────────────
        semantic_ranked: dict[int, tuple[int, float]] = {}
        faiss_results = _faiss_search(
            q_embedding, max(settings.rag_semantic_candidates, match_limit * 4)
        )
        for rank, (chunk_id, score) in enumerate(faiss_results.items()):
            semantic_ranked[chunk_id] = (rank + 1, score)

        # ── Keyword search (FTS5) ─────────────────────────
        keyword_ranked: dict[int, tuple[int, float]] = {}
        try:
            fts_query = " OR ".join(_query_terms(question)) or question
            fts_rows = conn.execute(
                """SELECT rowid, rank
                   FROM chunks_fts
                   WHERE chunks_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (fts_query, settings.rag_keyword_candidates),
            ).fetchall()
            for rank, fts_row in enumerate(fts_rows):
                keyword_ranked[fts_row["rowid"]] = (rank + 1, abs(float(fts_row["rank"])))
        except Exception:
            pass

        # File/title path matching for note-name queries
        terms = _query_terms(question)
        if terms:
            note_terms = [t for t in terms if "_" in t or "." in t or "-" in t]
            if note_terms:
                note_clauses = " OR ".join(
                    ["lower(d.path || ' ' || d.title) LIKE ?"] * len(note_terms)
                )
                note_params = [f"%{t}%" for t in note_terms]
                try:
                    note_rows = conn.execute(
                        f"""SELECT c.id
                            FROM chunks c
                            JOIN documents d ON d.id = c.document_id
                            WHERE {note_clauses}
                            ORDER BY c.chunk_index
                            LIMIT ?""",
                        [*note_params, settings.rag_context_limit],
                    ).fetchall()
                    for rank, note_row in enumerate(note_rows, start=1):
                        keyword_ranked[note_row["id"]] = (rank, 2.0)
                except Exception:
                    pass

            searchable = "lower(d.path || ' ' || d.title || ' ' || coalesce(c.heading, ''))"
            clauses = " OR ".join([f"{searchable} LIKE ?"] * len(terms))
            params = [f"%{t}%" for t in terms]
            term_score = " + ".join(
                [f"CASE WHEN {searchable} LIKE ? THEN 1 ELSE 0 END"] * len(terms)
            )
            try:
                path_rows = conn.execute(
                    f"""SELECT c.id, ({term_score}) AS term_hits
                        FROM chunks c
                        JOIN documents d ON d.id = c.document_id
                        WHERE {clauses}
                        ORDER BY term_hits DESC, c.chunk_index
                        LIMIT ?""",
                    [*params, *params, settings.rag_keyword_candidates],
                ).fetchall()
                for rank, path_row in enumerate(path_rows, start=1):
                    term_hits = int(path_row["term_hits"] or 0)
                    existing = keyword_ranked.get(path_row["id"])
                    if not existing or rank < existing[0]:
                        keyword_ranked[path_row["id"]] = (rank, float(term_hits))
            except Exception:
                pass

        # ── RRF Fusion ────────────────────────────────────
        k = settings.rag_rrf_k
        all_ids = set(semantic_ranked.keys()) | set(keyword_ranked.keys())
        fused: list[tuple[float, int]] = []
        for chunk_id in all_ids:
            score = 0.0
            if chunk_id in semantic_ranked:
                score += 1.0 / (k + semantic_ranked[chunk_id][0])
            if chunk_id in keyword_ranked:
                score += 1.0 / (k + keyword_ranked[chunk_id][0])
            fused.append((score, chunk_id))

        fused.sort(key=lambda x: x[0], reverse=True)
        top_ids = [cid for _, cid in fused[:match_limit]]

        if not top_ids:
            return []

        placeholders = ",".join("?" * len(top_ids))
        results = conn.execute(
            f"""SELECT c.id, c.chunk_index, c.heading, c.content,
                       c.token_estimate, d.path, d.title AS doc_title
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.id IN ({placeholders})""",
            top_ids,
        ).fetchall()

        result_map = {r["id"]: dict(r) for r in results}
        ordered: list[dict[str, Any]] = []
        for fused_score, chunk_id in fused[:match_limit]:
            if chunk_id in result_map:
                entry = result_map[chunk_id]
                entry["fused_score"] = fused_score
                entry["semantic_score"] = semantic_ranked.get(chunk_id, (0, 0.0))[1]
                entry["keyword_score"] = keyword_ranked.get(chunk_id, (0, 0.0))[1]
                ordered.append(entry)

    return ordered


def answer(question: str, *, model: str | None = None) -> dict[str, Any]:
    matches = search(question, limit=settings.rag_context_limit)
    context_parts: list[str] = []
    citations: list[dict[str, Any]] = []

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
            "chunk_index": match["chunk_index"],
            "score": float(match["fused_score"]),
        })

    system_prompt = (
        "Eres Eira Brain, un asistente de conocimiento personal. "
        "Respondes SOLO bas\u00e1ndote en el contexto proporcionado de la base de conocimiento del usuario. "
        "Si la respuesta no est\u00e1 en el contexto, dilo claramente. "
        "Cita las fuentes relevantes usando [Fuente N] inline. "
        "Responde en el mismo idioma en que te preguntan."
    )
    user_prompt = (
        f"Pregunta:\n{question}\n\n"
        f"Contexto:\n{chr(10).join(context_parts) if context_parts else 'No se encontr\u00f3 contexto relevante.'}"
    )

    client = get_ollama()
    response = client.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=model or settings.model_fast,
        temperature=0.3,
    )
    return {"answer": response, "citations": citations}
