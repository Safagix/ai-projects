from __future__ import annotations

import time

import pytest

from human_typer.profiles.models import TypingProfile
from human_typer.profiles.repository import ProfileRepository
from human_typer.profiles.trainer import TypingTrainer, _reject_outliers


class TestRejectOutliers:
    def test_no_outliers(self) -> None:
        data = [0.1, 0.12, 0.11, 0.13, 0.1]
        result = _reject_outliers(data)
        assert len(result) == len(data)

    def test_removes_extreme_values(self) -> None:
        data = [0.08, 0.09, 0.10, 0.11, 0.12] * 4 + [50.0, 100.0]
        result = _reject_outliers(data)
        assert len(result) < len(data)
        assert max(result) < 1.0

    def test_small_dataset_unchanged(self) -> None:
        data = [0.1, 0.5]
        result = _reject_outliers(data)
        assert result == data


class TestTypingTrainer:
    def test_rejects_insufficient_samples(
        self, default_profile: TypingProfile, repo: ProfileRepository
    ) -> None:
        trainer = TypingTrainer(default_profile, repository=repo)
        with pytest.raises(ValueError, match="Solo"):
            trainer.finalize(save=True)

    def test_trains_with_synthetic_data(
        self, default_profile: TypingProfile, repo: ProfileRepository
    ) -> None:
        trainer = TypingTrainer(default_profile, repository=repo)
        now = time.perf_counter()

        for i in range(100):
            trainer.on_key_down()
            time.sleep(0.001)
            trainer.on_key_up()
            time.sleep(0.08)

        result = trainer.finalize(save=True)
        assert result.training_samples >= 30
        assert result.char_interval_mean > 0
        assert result.char_interval_std >= 0

    def test_records_key_holds(
        self, default_profile: TypingProfile, repo: ProfileRepository
    ) -> None:
        trainer = TypingTrainer(default_profile, repository=repo)
        for _ in range(50):
            trainer.on_key_down()
            time.sleep(0.05)
            trainer.on_key_up()
            time.sleep(0.1)
        trainer.finalize(save=False)
        assert len(trainer._key_holds) > 0

    def test_records_pauses(
        self, default_profile: TypingProfile, repo: ProfileRepository
    ) -> None:
        trainer = TypingTrainer(default_profile, repository=repo)
        for _ in range(50):
            trainer.on_key_down()
            time.sleep(0.01)
            trainer.on_key_up()
            time.sleep(0.1)
        trainer.on_pause(0.5)
        trainer.on_pause(0.3)
        trainer.finalize(save=False)
        assert len(trainer._pauses) > 0
