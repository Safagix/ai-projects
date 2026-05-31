from __future__ import annotations

import math
import random

from human_typer.engine.distributions import truncated_gauss, uniform_jitter


class TestTruncatedGauss:
    def test_result_in_range(self) -> None:
        rng = random.Random(42)
        for _ in range(200):
            v = truncated_gauss(0.1, 0.05, 0.03, 0.5, rng=rng)
            assert 0.03 <= v <= 0.5

    def test_deterministic_with_seed(self) -> None:
        rng1 = random.Random(7)
        rng2 = random.Random(7)
        vals1 = [truncated_gauss(0.1, 0.03, 0.01, 0.3, rng=rng1) for _ in range(50)]
        vals2 = [truncated_gauss(0.1, 0.03, 0.01, 0.3, rng=rng2) for _ in range(50)]
        assert vals1 == vals2

    def test_zero_sigma_returns_mu(self) -> None:
        v = truncated_gauss(0.1, 0.0, 0.01, 0.3, rng=random.Random(42))
        assert v == 0.1

    def test_swapped_bounds(self) -> None:
        v = truncated_gauss(0.1, 0.03, 0.5, 0.03, rng=random.Random(42))
        assert v == 0.5

    def test_mean_close_to_mu(self) -> None:
        rng = random.Random(42)
        samples = [truncated_gauss(0.2, 0.04, 0.05, 0.4, rng=rng) for _ in range(2000)]
        avg = sum(samples) / len(samples)
        assert abs(avg - 0.2) < 0.02


class TestUniformJitter:
    def test_result_in_range(self) -> None:
        rng = random.Random(42)
        for _ in range(200):
            v = uniform_jitter(0.5, 0.2, rng=rng)
            assert 0.4 <= v <= 0.6

    def test_deterministic_with_seed(self) -> None:
        rng1 = random.Random(3)
        rng2 = random.Random(3)
        vals1 = [uniform_jitter(1.0, 0.5, rng=rng1) for _ in range(20)]
        vals2 = [uniform_jitter(1.0, 0.5, rng=rng2) for _ in range(20)]
        assert vals1 == vals2
