"""Writer — Create new Markdown notes in the Obsidian Vault."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from local_rag.config import settings
from local_rag.indexer import ingest_single_file
from local_rag.ollama_client import get_ollama

TITLE_PROMPT = """Given the user's note content below, generate:
1. A short filename in snake_case (no extension, max 5 words)
2. 2-4 relevant tags as a comma-separated list

Reply in EXACTLY this format, nothing else:
FILENAME: the_filename
TAGS: tag1, tag2, tag3

User content:
{content}"""


def _sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:60] or "nota_sin_titulo"


def _generate_metadata(content: str) -> tuple[str, list[str]]:
    """Use LLM to generate a filename and tags for the note."""
    client = get_ollama()
    try:
        raw = client.chat(
            [
                {"role": "system", "content": "You are a helpful assistant that generates metadata for notes."},
                {"role": "user", "content": TITLE_PROMPT.format(content=content[:500])},
            ],
            model=settings.model_fast,
            temperature=0.3,
        )
        filename = "nota_sin_titulo"
        tags: list[str] = []
        for line in raw.splitlines():
            line = line.strip()
            if line.upper().startswith("FILENAME:"):
                filename = _sanitize_filename(line.split(":", 1)[1].strip())
            elif line.upper().startswith("TAGS:"):
                tags = [t.strip().lower().replace(" ", "-") for t in line.split(":", 1)[1].split(",") if t.strip()]
        return filename, tags
    except Exception:
        return "nota_sin_titulo", ["sin-clasificar"]


def write_note(content: str, *, title: str | None = None) -> dict:
    """Write a new Markdown note to the Obsidian Vault inbox folder."""

    # Ensure the inbox folder exists
    inbox = settings.obsidian_inbox_path
    inbox.mkdir(parents=True, exist_ok=True)

    # Generate or use provided title
    if title:
        filename = _sanitize_filename(title)
        tags = []
    else:
        filename, tags = _generate_metadata(content)

    # Avoid overwriting
    target = inbox / f"{filename}.md"
    counter = 1
    while target.exists():
        target = inbox / f"{filename}_{counter}.md"
        counter += 1

    # Build the note
    now = datetime.now()
    frontmatter_lines = [
        "---",
        f"created: {now.strftime('%Y-%m-%d %H:%M')}",
        f"source: Eira Brain Chat",
    ]
    if tags:
        frontmatter_lines.append(f"tags: [{', '.join(tags)}]")
    frontmatter_lines.append("---")
    frontmatter_lines.append("")

    body = "\n".join(frontmatter_lines) + f"# {filename.replace('_', ' ').title()}\n\n{content}\n"

    # Write file
    target.write_text(body, encoding="utf-8")

    # Auto-index into the RAG database
    try:
        ingest_single_file(str(target))
    except Exception:
        pass  # Non-critical; will be indexed on next full ingest

    return {
        "status": "saved",
        "path": str(target),
        "filename": target.name,
        "tags": tags,
        "folder": str(inbox),
    }
