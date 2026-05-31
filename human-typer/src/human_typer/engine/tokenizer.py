from __future__ import annotations

import dataclasses
import unicodedata


@dataclasses.dataclass(frozen=True, slots=True)
class Token:
    text: str
    kind: str  # "word", "space", "newline", "punctuation"
    is_sentence_end: bool = False


_PUNCTUATION = frozenset(".,!?;:()[]{}\"'/\u201c\u201d\u2018\u2019\u2014\u2013\u2026")
_SENTENCE_END = frozenset({".", "!", "?", "\u2026"})


def tokenize(text: str) -> list[Token]:
    if not text:
        return []
    tokens: list[Token] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if ch == "\n":
            tokens.append(Token(text="\n", kind="newline"))
            i += 1
            continue

        if ch in (" ", "\t", "\r"):
            start = i
            while i < n and text[i] in (" ", "\t", "\r"):
                i += 1
            tokens.append(Token(text=text[start:i], kind="space"))
            continue

        cat = unicodedata.category(ch)
        if cat.startswith("P") or cat.startswith("S"):
            start = i
            while i < n and (
                unicodedata.category(text[i]).startswith(("P", "S"))
            ):
                i += 1
            token_text = text[start:i]
            is_end = token_text[-1] in _SENTENCE_END if token_text else False
            tokens.append(Token(text=token_text, kind="punctuation", is_sentence_end=is_end))
            continue

        start = i
        while i < n and text[i] not in ("\n", " ", "\t", "\r") and not (
            unicodedata.category(text[i]).startswith(("P", "S"))
        ):
            i += 1
        tokens.append(Token(text=text[start:i], kind="word"))

    return tokens
