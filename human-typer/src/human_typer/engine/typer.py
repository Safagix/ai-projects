from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import Any

from human_typer.config import SLEEP_POLL_INTERVAL
from human_typer.engine.distributions import sleep_granular, truncated_gauss, uniform_jitter
from human_typer.engine.normalize import strip_accents
from human_typer.engine.tokenizer import Token, tokenize
from human_typer.engine.typo import TypoStrategy
from human_typer.io.protocol import KeyboardBackend
from human_typer.profiles.models import TypingProfile


ProgressCallback = Callable[[int, int, str], None]


class HumanTyper:
    def __init__(
        self,
        backend: KeyboardBackend,
        profile: TypingProfile,
        *,
        typo_strategy: TypoStrategy | None = None,
        stealth: bool = False,
        speed_multiplier: float = 1.0,
        rng: random.Random | None = None,
    ) -> None:
        self._backend = backend
        self._profile = profile
        self._typo = typo_strategy or TypoStrategy(probability=profile.typo_probability)
        self._stealth = stealth
        self._speed_multiplier = max(0.1, min(5.0, speed_multiplier))
        self._rng = rng or random

        self._paused = False
        self._stopped = False

    # -- control ---------------------------------------------------------------

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def toggle_pause(self) -> bool:
        self._paused = not self._paused
        return self._paused

    def stop(self) -> None:
        self._stopped = True
        self._paused = False

    @property
    def speed_multiplier(self) -> float:
        return self._speed_multiplier

    @speed_multiplier.setter
    def speed_multiplier(self, value: float) -> None:
        self._speed_multiplier = max(0.1, min(5.0, value))

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_stopped(self) -> bool:
        return self._stopped

    # -- core -----------------------------------------------------------------

    def type_text(
        self,
        text: str,
        *,
        start_pos: int | None = None,
        end_pos: int | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        self._stopped = False
        self._paused = False

        if start_pos is not None and start_pos < 0:
            start_pos = 0
        if end_pos is not None and end_pos < 0:
            end_pos = 0

        if start_pos is not None and end_pos is not None and start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        working_text = text
        if start_pos is not None:
            working_text = working_text[start_pos:]
        if end_pos is not None:
            working_text = working_text[: end_pos - (start_pos or 0)]

        tokens = tokenize(strip_accents(working_text))
        total = len(working_text)
        char_count_since_medium = 0
        char_count_since_long = 0
        char_index = 0

        p = self._profile

        for token in tokens:
            if self._stopped:
                break

            if token.kind == "newline":
                self._backend.press("\n")
                self._delay(truncated_gauss(0.080, 0.030, 0.030, 0.250, rng=self._rng))
                continue

            if token.kind == "space":
                pause = self._space_pause()
                self._delay(pause)
                self._backend.press(" ")
                self._delay(truncated_gauss(0.050, 0.020, 0.015, 0.150, rng=self._rng))
                continue

            if token.kind == "punctuation":
                for ch in token.text:
                    if self._stopped:
                        break
                    interval = truncated_gauss(
                        p.char_interval_mean, p.char_interval_std, 0.030, 0.400, rng=self._rng
                    )
                    if self._rng.random() < 0.15:
                        interval *= max(0.5, self._rng.gauss(1.0, 0.12))
                    self._delay(interval)
                    self._type_character(ch)
                    char_count_since_medium += 1
                    char_count_since_long += 1
                    char_index += 1
                    if on_progress:
                        on_progress(char_index, total, "typing")

                if token.is_sentence_end:
                    pause = truncated_gauss(
                        p.sentence_end_pause, 0.080, 0.100, 0.800, rng=self._rng
                    )
                    self._delay(pause)
                continue

            # token.kind == "word"
            slowdown = self._word_slowdown(len(token.text))
            for ch in token.text:
                if self._stopped:
                    break

                interval = truncated_gauss(
                    p.char_interval_mean, p.char_interval_std, 0.020, 0.450, rng=self._rng
                )
                interval *= slowdown
                if self._rng.random() < 0.15:
                    interval *= max(0.5, self._rng.gauss(1.0, 0.12))
                self._delay(interval)

                if self._typo.should_typo():
                    typo_char = self._typo.generate(ch)
                    if typo_char is not None:
                        self._backend.press(typo_char)
                        correction_delay = truncated_gauss(
                            p.typo_correction_delay_mean,
                            p.typo_correction_delay_std,
                            0.080,
                            0.600,
                            rng=self._rng,
                        )
                        self._delay(correction_delay)
                        self._press_backspace()
                        self._delay(truncated_gauss(0.080, 0.030, 0.030, 0.200, rng=self._rng))

                self._type_character(ch)
                char_count_since_medium += 1
                char_count_since_long += 1
                char_index += 1
                if on_progress:
                    on_progress(char_index, total, "typing")

                if self._stopped:
                    break

            if self._stopped:
                break

            if char_count_since_long >= p.long_pause_every and self._rng.random() < 0.6:
                pause = truncated_gauss(
                    p.long_pause_mean, p.long_pause_std, 0.800, 6.0, rng=self._rng
                )
                if self._stealth:
                    pause = uniform_jitter(pause, 0.60, rng=self._rng)
                self._delay(pause)
                char_count_since_long = 0
                char_count_since_medium = 0
            elif char_count_since_medium >= p.medium_pause_every and self._rng.random() < 0.5:
                pause = truncated_gauss(
                    p.medium_pause_mean, p.medium_pause_std, 0.200, 1.5, rng=self._rng
                )
                if self._stealth:
                    pause = uniform_jitter(pause, 0.50, rng=self._rng)
                self._delay(pause)
                char_count_since_medium = 0

    # -- internal -------------------------------------------------------------

    def _delay(self, seconds: float) -> None:
        effective = seconds / self._speed_multiplier
        if effective <= 0:
            return
        while effective > 0 and not self._stopped:
            while self._paused and not self._stopped:
                time.sleep(SLEEP_POLL_INTERVAL)
            if self._stopped:
                return
            chunk = min(SLEEP_POLL_INTERVAL, effective)
            time.sleep(chunk)
            effective -= chunk

    def _type_character(self, ch: str) -> None:
        hold = truncated_gauss(
            self._profile.key_hold_mean,
            self._profile.key_hold_std,
            0.015,
            0.300,
            rng=self._rng,
        )
        self._backend.key_down(ch)
        time.sleep(hold)
        self._backend.key_up(ch)

    def _press_backspace(self) -> None:
        hold = self._rng.uniform(0.030, 0.080)
        self._backend.key_down("backspace")
        time.sleep(hold)
        self._backend.key_up("backspace")

    def _space_pause(self) -> float:
        p = self._profile
        if self._rng.random() < 0.3:
            return truncated_gauss(p.word_pause_mean, p.word_pause_std, 0.030, 0.600, rng=self._rng)
        return self._rng.uniform(p.word_pause_mean * 0.6, p.word_pause_mean * 1.4)

    def _word_slowdown(self, word_len: int) -> float:
        if word_len >= self._profile.long_word_threshold:
            return self._profile.long_word_slowdown
        return 1.0
