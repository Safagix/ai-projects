from __future__ import annotations

import unicodedata


def strip_accents(text: str) -> str:
    result: list[str] = []
    for ch in text:
        if ch in ("\u00f1", "\u00d1"):
            result.append(ch)
            continue
        decomposed = unicodedata.normalize("NFKD", ch)
        base = ""
        for d in decomposed:
            if not unicodedata.category(d).startswith("M"):
                base = d
        result.append(base or ch)
    return "".join(result)
