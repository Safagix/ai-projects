from __future__ import annotations

import random

LayoutMap = dict[str, str]

QWERTY_NEIGHBORS: LayoutMap = {
    "a": "qwszx",
    "b": "vghn",
    "c": "xdfv",
    "d": "serfcx",
    "e": "wsdfr",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "i": "ujklo",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kiop",
    "m": "njki",
    "n": "bhjm",
    "o": "iklp",
    "p": "ol",
    "q": "wsa",
    "r": "edfgt",
    "s": "awedxz",
    "t": "rfghy",
    "u": "yhjki",
    "v": "cfgb",
    "w": "qase",
    "x": "zsdc",
    "y": "tghju",
    "z": "asx",
}

QWERTY_NEIGHBORS_UPPER = {k.upper(): v.upper() for k, v in QWERTY_NEIGHBORS.items()}

_FULL_LAYOUT = {**QWERTY_NEIGHBORS, **QWERTY_NEIGHBORS_UPPER}


class TypoStrategy:
    def __init__(
        self,
        probability: float = 0.025,
        layout: LayoutMap | None = None,
        *,
        rng: random.Random | None = None,
    ) -> None:
        self.probability = probability
        self._layout = layout or _FULL_LAYOUT
        self._rng = rng or random

    def should_typo(self) -> bool:
        return self._rng.random() < self.probability

    def generate(self, char: str) -> str | None:
        entry = self._layout.get(char)
        if entry is None:
            return None
        return self._rng.choice(entry)
