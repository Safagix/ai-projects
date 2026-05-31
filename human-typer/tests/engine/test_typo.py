from __future__ import annotations

import random

from human_typer.engine.typo import QWERTY_NEIGHBORS, TypoStrategy


class TestTypoStrategy:
    def test_should_typo_with_zero_probability(self) -> None:
        s = TypoStrategy(probability=0.0, rng=random.Random(42))
        for _ in range(1000):
            assert not s.should_typo()

    def test_should_typo_with_probability_one(self) -> None:
        s = TypoStrategy(probability=1.0, rng=random.Random(42))
        for _ in range(1000):
            assert s.should_typo()

    def test_generate_returns_neighbor(self) -> None:
        rng = random.Random(42)
        s = TypoStrategy(probability=0.1, rng=rng)
        neighbors = set(QWERTY_NEIGHBORS["a"])
        found = set()
        for _ in range(50):
            result = s.generate("a")
            if result is not None:
                found.add(result.lower())
        assert found, "Deberia generar algun typo"
        assert found.issubset(neighbors)

    def test_generate_returns_none_for_unknown_char(self) -> None:
        s = TypoStrategy()
        assert s.generate("1") is None
        assert s.generate(" ") is None
        assert s.generate("\n") is None

    def test_num_typo_is_none(self) -> None:
        s = TypoStrategy()
        assert s.generate("5") is None

    def test_uppercase_preserved(self) -> None:
        rng = random.Random(42)
        s = TypoStrategy(probability=1.0, rng=rng)
        for _ in range(30):
            result = s.generate("A")
            if result is not None:
                assert result.isupper()

    def test_consistent_with_rng_seed(self) -> None:
        s1 = TypoStrategy(rng=random.Random(99))
        s2 = TypoStrategy(rng=random.Random(99))
        results1 = [s1.generate("a") for _ in range(20)]
        results2 = [s2.generate("a") for _ in range(20)]
        assert results1 == results2
