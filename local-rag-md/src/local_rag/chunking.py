from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class Chunk:
    chunk_index: int
    heading: str
    content: str
    token_estimate: int
    meta: dict[str, Any] | None = None


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    meta: dict[str, Any] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    value = json.loads(value.replace("'", '"'))
                except Exception:
                    value = [v.strip().strip("'\"") for v in value.strip("[]").split(",")]
            meta[key] = value
    return meta, body


def _split_paragraphs(text: str, max_chars: int, overlap: int = 0) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        extra = len(paragraph) + (2 if current else 0)
        if current and current_len + extra > max_chars:
            chunks.append("\n\n".join(current).strip())
            if overlap > 0 and len(current) >= 2:
                current = [current[-1]]
                current_len = len(current[-1])
            else:
                current = []
                current_len = 0
        current.append(paragraph)
        current_len += extra

    if current:
        chunks.append("\n\n".join(current).strip())

    return chunks


def chunk_markdown(
    text: str,
    *,
    max_chars: int = 1800,
    overlap: int = 0,
) -> list[Chunk]:
    frontmatter, body = extract_frontmatter(text)
    title = frontmatter.get("title") or frontmatter.get("aliases")
    if isinstance(title, list):
        title = title[0]

    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_heading = str(title) if title else "Document"
    current_lines: list[str] = []

    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = match.group(2).strip() or "Untitled"
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    chunks: list[Chunk] = []
    chunk_index = 0

    for heading, section_lines in sections:
        body_text = "\n".join(section_lines).strip()
        if not body_text:
            continue
        for piece in _split_paragraphs(body_text, max_chars=max_chars, overlap=overlap):
            chunk = Chunk(
                chunk_index=chunk_index,
                heading=heading,
                content=piece,
                token_estimate=estimate_tokens(piece),
                meta=dict(frontmatter) if frontmatter else None,
            )
            chunks.append(chunk)
            chunk_index += 1

    return chunks
