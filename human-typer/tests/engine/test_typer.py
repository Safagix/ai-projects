from __future__ import annotations

import random
from collections.abc import Callable

import pytest

from human_typer.engine.tokenizer import tokenize
from human_typer.engine.typer import HumanTyper
from human_typer.engine.typo import TypoStrategy
from human_typer.io.protocol import KeyboardBackend
from human_typer.profiles.models import TypingProfile


class SpyBackend(KeyboardBackend):
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def key_down(self, key: str) -> None:
        self.events.append(("down", key))

    def key_up(self, key: str) -> None:
        self.events.append(("up", key))

    def press(self, key: str) -> None:
        self.events.append(("press", key))

    @property
    def press_sequence(self) -> str:
        return "".join(
            key for action, key in self.events if action == "press"
        )


class TestHumanTyper:
    @pytest.fixture
    def backend(self) -> SpyBackend:
        return SpyBackend()

    @pytest.fixture
    def profile(self) -> TypingProfile:
        return TypingProfile(
            typo_probability=0.0,
            char_interval_mean=0.05,
            char_interval_std=0.01,
            word_pause_mean=0.08,
            medium_pause_every=100,
            long_pause_every=500,
            key_hold_mean=0.03,
            key_hold_std=0.005,
            long_word_threshold=20,
        )

    @pytest.fixture
    def typer(self, backend: SpyBackend, profile: TypingProfile) -> HumanTyper:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        return HumanTyper(backend, profile, typo_strategy=typo, rng=rng)

    def test_press_sequence_simple_word(self, typer: HumanTyper, backend: SpyBackend) -> None:
        typer.type_text("hola")
        presses = backend.press_sequence
        assert "h" in presses or any(
            action in ("down", "up") and key == "h"
            for action, key in backend.events
        )

    def test_start_pos_slice(self, typer: HumanTyper, backend: SpyBackend) -> None:
        typer.type_text("abcdef", start_pos=3)
        pressed = [key for action, key in backend.events if action in ("down", "press")]
        assert all(k in "def" for k in pressed if len(k) == 1)

    def test_stop_mid_typing(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng)

        long_profile = profile.model_copy(
            update={"char_interval_mean": 0.5, "char_interval_std": 0.01}
        )
        typer2 = HumanTyper(backend, long_profile, typo_strategy=typo, rng=rng)

        import threading

        def stop_after_delay() -> None:
            import time
            time.sleep(0.3)
            typer2.stop()

        t = threading.Thread(target=stop_after_delay, daemon=True)
        t.start()
        typer2.type_text("aaaaaaaaaa")
        assert typer2.is_stopped

    def test_pause_and_resume(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng)
        typer.pause()
        assert typer.is_paused
        typer.resume()
        assert not typer.is_paused

    def test_toggle_pause(self, typer: HumanTyper) -> None:
        assert typer.toggle_pause() is True
        assert typer.toggle_pause() is False

    def test_speed_multiplier_bounds(self, typer: HumanTyper) -> None:
        typer.speed_multiplier = 10.0
        assert typer.speed_multiplier == 5.0
        typer.speed_multiplier = -1.0
        assert typer.speed_multiplier == 0.1

    def test_text_with_newlines(self, typer: HumanTyper, backend: SpyBackend) -> None:
        typer.type_text("a\nb")
        newline_count = sum(1 for _, key in backend.events if key == "\n")
        assert newline_count >= 1

    def test_accent_stripping_applied(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng)
        typer.type_text("canci\u00f3n")
        pressed = [key for action, key in backend.events if action == "down"]
        assert "\u00f3" not in pressed
        assert "o" in pressed

    def test_n_preserved_in_accent_stripping(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng)
        typer.type_text("ni\u00f1o")
        pressed = [key for action, key in backend.events if action == "down"]
        assert "\u00f1" in pressed

    def test_speed_multiplier_via_constructor(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng, speed_multiplier=2.5)
        assert typer.speed_multiplier == 2.5

    def test_speed_clamped_in_constructor(self, backend: SpyBackend, profile: TypingProfile) -> None:
        rng = random.Random(42)
        typo = TypoStrategy(probability=profile.typo_probability, rng=rng)
        typer = HumanTyper(backend, profile, typo_strategy=typo, rng=rng, speed_multiplier=10.0)
        assert typer.speed_multiplier == 5.0

    def test_tokenizer_integration(self) -> None:
        tokens = tokenize("Hola mundo.")
        kinds = [t.kind for t in tokens]
        assert kinds == ["word", "space", "word", "punctuation"]
