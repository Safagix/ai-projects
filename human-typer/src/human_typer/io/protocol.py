from __future__ import annotations

from abc import ABC, abstractmethod


class KeyboardBackend(ABC):
    @abstractmethod
    def key_down(self, key: str) -> None: ...

    @abstractmethod
    def key_up(self, key: str) -> None: ...

    @abstractmethod
    def press(self, key: str) -> None: ...
