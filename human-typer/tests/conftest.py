from __future__ import annotations

import random
import tempfile
from pathlib import Path

import pytest

from human_typer.profiles.models import TypingProfile
from human_typer.profiles.repository import ProfileRepository


@pytest.fixture
def default_profile() -> TypingProfile:
    return TypingProfile()


@pytest.fixture
def trained_profile() -> TypingProfile:
    return TypingProfile(
        name="test_profile",
        training_samples=150,
        char_interval_mean=0.095,
        char_interval_std=0.038,
        key_hold_mean=0.058,
        key_hold_std=0.022,
        typo_probability=0.03,
    )


@pytest.fixture
def seeded_rng() -> random.Random:
    return random.Random(42)


@pytest.fixture
def temp_profiles_dir() -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def repo(temp_profiles_dir: Path) -> ProfileRepository:
    return ProfileRepository(base_dir=temp_profiles_dir)
