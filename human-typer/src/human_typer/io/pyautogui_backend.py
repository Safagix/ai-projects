from __future__ import annotations

from human_typer.io.protocol import KeyboardBackend


class PyAutoGuiBackend(KeyboardBackend):
    def __init__(self) -> None:
        import pyautogui

        self._pg = pyautogui

    def key_down(self, key: str) -> None:
        self._pg.keyDown(key)

    def key_up(self, key: str) -> None:
        self._pg.keyUp(key)

    def press(self, key: str) -> None:
        self._pg.write(key, interval=0.0)
