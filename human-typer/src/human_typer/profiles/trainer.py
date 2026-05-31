from __future__ import annotations

import math
import statistics
import time
from collections.abc import Callable

from human_typer.config import MIN_TRAINING_SAMPLES
from human_typer.profiles.models import TypingProfile
from human_typer.profiles.repository import ProfileRepository


def _reject_outliers(data: list[float], iqr_mult: float = 2.0) -> list[float]:
    if len(data) < 4:
        return data
    sorted_data = sorted(data)
    q1_index = len(sorted_data) // 4
    q3_index = (3 * len(sorted_data)) // 4
    q1 = sorted_data[q1_index]
    q3 = sorted_data[q3_index]
    iqr = q3 - q1
    if iqr <= 0:
        return data
    lower = q1 - iqr_mult * iqr
    upper = q3 + iqr_mult * iqr
    return [x for x in data if lower <= x <= upper]


def _median(data: list[float]) -> float:
    if not data:
        return 0.0
    return statistics.median(data)


class TypingTrainer:
    def __init__(
        self,
        profile: TypingProfile,
        repository: ProfileRepository | None = None,
    ) -> None:
        self.profile = profile
        self._repo = repository or ProfileRepository()

        self._intervals: list[float] = []
        self._key_holds: list[float] = []
        self._pauses: list[float] = []

        self._last_event: float | None = None
        self._key_down_time: float | None = None

    def on_key_down(self) -> None:
        now = time.perf_counter()
        if self._last_event is not None:
            elapsed = now - self._last_event
            if 0.005 < elapsed < 5.0:
                self._intervals.append(elapsed)
        self._last_event = now
        self._key_down_time = now

    def on_key_up(self) -> None:
        if self._key_down_time is not None:
            hold = time.perf_counter() - self._key_down_time
            if 0.005 <= hold <= 0.500:
                self._key_holds.append(hold)
            self._key_down_time = None

    def on_pause(self, duration: float) -> None:
        if 0.020 <= duration <= 5.0:
            self._pauses.append(duration)

    def finalize(self, *, save: bool = True) -> TypingProfile:
        intervals = _reject_outliers(self._intervals)
        key_holds = _reject_outliers(self._key_holds)
        pauses = _reject_outliers(self._pauses)

        n = len(intervals)
        if n < MIN_TRAINING_SAMPLES:
            raise ValueError(
                f"Solo {n} muestras v\u00e1lidas (m\u00ednimo {MIN_TRAINING_SAMPLES}). "
                "Perfil no actualizado."
            )

        self.profile.char_interval_mean = statistics.mean(intervals)
        self.profile.char_interval_std = statistics.stdev(intervals) if n > 1 else 0.02

        if key_holds:
            self.profile.key_hold_mean = statistics.mean(key_holds)
            self.profile.key_hold_std = (
                statistics.stdev(key_holds) if len(key_holds) > 1 else 0.01
            )

        if pauses:
            self.profile.word_pause_mean = _median(pauses)

        self.profile.training_samples = n

        if save:
            self._repo.save(self.profile)
        return self.profile
