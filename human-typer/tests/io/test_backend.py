from __future__ import annotations

import pytest

from human_typer.io.protocol import KeyboardBackend


class TestKeyboardBackendProtocol:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            KeyboardBackend()  # type: ignore[abstract]

    def test_subclass_must_implement_all(self) -> None:
        class Incomplete(KeyboardBackend):
            def key_down(self, key: str) -> None:
                pass

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]
