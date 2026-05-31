"""UI/UX Collector — Ingest and catalog UI/UX components via LLM classification."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from local_rag.config import settings
from local_rag.ollama_client import get_ollama

CLASSIFIER_PROMPT = """You are a UI/UX component catalog manager. Analyze the following component and output a JSON object with these fields:

- name: The component's name (exactly as provided)
- category: One of [button, card, modal, navbar, sidebar, form, chart, layout, animation, loader, hero, footer, gallery, table, input, typography, icon, tooltip, menu, carousel, tab, accordion, badge, avatar, breadcrumb, pagination, progress, skeleton, toast, dialog, drawer, other]
- tags: Array of 2-5 lowercase tags describing the component (e.g., ["css", "hover-effect", "glassmorphism"])
- description: A concise 1-2 sentence description of what the component does
- code_type: The type of code (html, css, js, react, vue, svelte, tailwind, bootstrap, pure-css, svg, canvas, threejs, webgl, python)
- quality_score: A score from 1-10 rating code quality, reusability, and completeness
- is_duplicate: false (always false — the caller handles duplicate detection)

Respond ONLY with valid JSON, no markdown, no explanation.

Component to analyze:
Name: {name}
Description: {description}
Code:
{code}"""


def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:60] or "component_sin_nombre"


def _load_catalog() -> list[dict]:
    catalog_path = Path(settings.uiux_catalog_path)
    if not catalog_path.exists():
        return []
    try:
        return json.loads(catalog_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_catalog(catalog: list[dict]) -> None:
    catalog_path = Path(settings.uiux_catalog_path)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = catalog_path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    temp_path.replace(catalog_path)


def _check_duplicate(name: str, code: str, catalog: list[dict]) -> dict | None:
    code_normalized = re.sub(r"\s+", "", code.lower())
    for item in catalog:
        if item.get("name", "").lower() == name.lower():
            return item
        existing_code = item.get("code", "")
        existing_normalized = re.sub(r"\s+", "", existing_code.lower())
        if len(code_normalized) > 10 and code_normalized in existing_normalized:
            return item
        if len(existing_normalized) > 10 and existing_normalized in code_normalized:
            return item
    return None


def _parse_llm_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    result: dict[str, Any] = {}
    fields = {
        "name": r'"name"\s*:\s*"([^"]*)"',
        "category": r'"category"\s*:\s*"([^"]*)"',
        "code_type": r'"code_type"\s*:\s*"([^"]*)"',
        "description": r'"description"\s*:\s*"([^"]*)"',
        "quality_score": r'"quality_score"\s*:\s*(\d+)',
    }
    for key, pattern in fields.items():
        match = re.search(pattern, raw)
        if match:
            result[key] = match.group(1)
            if key == "quality_score":
                result[key] = int(result[key])

    tags_match = re.search(r'"tags"\s*:\s*\[([^\]]*)\]', raw)
    if tags_match:
        result["tags"] = [
            t.strip().strip('"').lower()
            for t in tags_match.group(1).split(",")
            if t.strip()
        ]

    result.setdefault("is_duplicate", False)
    result.setdefault("duplicate_of", None)

    return result


def _write_obsidian_note(component: dict) -> str:
    folder = Path(settings.obsidian_uiux_folder)
    folder.mkdir(parents=True, exist_ok=True)

    filename = _sanitize_filename(component.get("name", "component"))
    target = folder / f"{filename}.md"
    counter = 1
    while target.exists():
        target = folder / f"{filename}_{counter}.md"
        counter += 1

    now = datetime.now()
    tags = component.get("tags", [])
    category = component.get("category", "other")
    code_type = component.get("code_type", "unknown")
    quality = component.get("quality_score", 0)
    description = component.get("description", "")
    code = component.get("code", "")
    name_val = component.get("name", "Unknown")

    frontmatter = [
        "---",
        "type: uiux-component",
        f"name: {name_val}",
        f"category: {category}",
        f"tags: [{', '.join(tags)}]",
        f"code_type: {code_type}",
        f"quality_score: {quality}",
        f"created: {now.strftime('%Y-%m-%d %H:%M')}",
        "source: Eira Brain UI/UX Collector",
        "---",
        "",
    ]

    body_lines = [
        f"# {name_val}",
        "",
        f"**Category:** {category} | **Type:** {code_type} | **Quality:** {quality}/10",
        "",
        description,
        "",
        "## Code",
        "",
        f"```{code_type}",
        code,
        "```",
        "",
    ]

    content = "\n".join(frontmatter) + "\n".join(body_lines)
    target.write_text(content, encoding="utf-8")

    return str(target)


def _guess_code_type(code: str) -> str:
    code_lower = code.lower()
    if (
        "react" in code_lower
        or "usestate" in code_lower
        or "useeffect" in code_lower
        or "jsx" in code_lower
    ):
        return "react"
    if "vue" in code_lower or "v-bind" in code_lower or "v-if" in code_lower:
        return "vue"
    if "svelte" in code_lower:
        return "svelte"
    if (
        "tailwind" in code_lower
        or 'classname="' in code_lower
        and 'class="' not in code_lower
    ):
        return "tailwind"
    if "<template" in code_lower or "<div" in code_lower or "</" in code_lower:
        return "html"
    if "def " in code_lower or "import " in code_lower:
        return "python"
    if (
        "function" in code_lower
        or "const " in code_lower
        or "let " in code_lower
        or "=>" in code_lower
    ):
        return "js"
    if (
        "@keyframes" in code_lower
        or "transition:" in code_lower
        or "animation:" in code_lower
    ):
        return "css"
    return "unknown"


def collect_component(
    name: str,
    description: str,
    code: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    if not name.strip():
        return {"status": "error", "message": "Name is required"}
    if not code.strip():
        return {"status": "error", "message": "Code is required"}

    catalog = _load_catalog()

    if not force:
        existing = _check_duplicate(name, code, catalog)
        if existing:
            return {
                "status": "duplicate",
                "message": f"Component '{existing.get('name')}' already exists in catalog",
                "existing_name": existing.get("name"),
                "suggest_confirm": True,
            }

    client = get_ollama()
    llm_response = ""
    parsed: dict[str, Any] = {}
    llm_error: str | None = None

    try:
        prompt = CLASSIFIER_PROMPT.format(
            name=name,
            description=description or "No description provided",
            code=code[:3000],
        )
        llm_response = client.chat(
            [
                {
                    "role": "system",
                    "content": "You are a UI/UX catalog manager. Output ONLY valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            model=settings.model_fast,
            temperature=0.1,
        )
        parsed = _parse_llm_response(llm_response)
    except Exception as e:
        llm_error = str(e)
        parsed = {
            "name": name,
            "category": "other",
            "tags": ["sin-clasificar"],
            "description": description or "",
            "code_type": _guess_code_type(code),
            "quality_score": 5,
            "is_duplicate": False,
            "duplicate_of": None,
        }

    component: dict[str, Any] = {
        "name": name.strip(),
        "category": parsed.get("category", "other"),
        "tags": parsed.get("tags", []) or ["sin-clasificar"],
        "description": parsed.get("description", description or ""),
        "code": code,
        "code_type": parsed.get("code_type", _guess_code_type(code)),
        "quality_score": int(
            parsed.get("quality_score", 5)
            if isinstance(parsed.get("quality_score"), (int, float))
            else 5
        ),
        "created_at": datetime.now().isoformat(),
    }

    catalog.append(component)
    _save_catalog(catalog)

    obsidian_path = ""
    try:
        obsidian_path = _write_obsidian_note(component)
    except Exception:
        pass

    result: dict[str, Any] = {
        "status": "saved",
        "component": {k: v for k, v in component.items() if k != "code"},
        "code_length": len(code),
        "obsidian_path": obsidian_path,
        "catalog_count": len(catalog),
    }

    if llm_error:
        result["status"] = "saved_with_warning"
        result["warning"] = (
            f"LLM classification failed ({llm_error}). Used fallback metadata."
        )
        result["llm_raw"] = llm_response

    return result
