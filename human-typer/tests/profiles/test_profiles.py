from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from human_typer.profiles.models import TypingProfile
from human_typer.profiles.repository import ProfileRepository


class TestTypingProfile:
    def test_default_values(self) -> None:
        p = TypingProfile()
        assert p.name == "default"
        assert p.char_interval_mean == 0.110
        assert p.training_samples == 0

    def test_rejects_negative_probability(self) -> None:
        with pytest.raises(ValidationError):
            TypingProfile(typo_probability=-0.1)

    def test_rejects_probability_over_max(self) -> None:
        with pytest.raises(ValidationError):
            TypingProfile(typo_probability=0.5)

    def test_rejects_inverted_pause_ordering(self) -> None:
        with pytest.raises(ValidationError):
            TypingProfile(
                long_pause_mean=0.3,
                medium_pause_mean=0.5,
            )

    def test_rejects_inverted_pause_every(self) -> None:
        with pytest.raises(ValidationError):
            TypingProfile(
                long_pause_every=5,
                medium_pause_every=10,
            )

    def test_valid_custom_profile(self) -> None:
        p = TypingProfile(
            name="fast",
            char_interval_mean=0.065,
            char_interval_std=0.020,
            training_samples=500,
        )
        assert p.name == "fast"
        assert p.char_interval_mean == 0.065

    def test_serialization_roundtrip(self) -> None:
        p = TypingProfile(name="roundtrip", typo_probability=0.05, training_samples=100)
        data = p.model_dump()
        restored = TypingProfile(**data)
        assert restored.name == p.name
        assert restored.typo_probability == p.typo_probability

    def test_model_dump_json(self) -> None:
        p = TypingProfile(name="json_test")
        json_str = p.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["name"] == "json_test"
        assert parsed["char_interval_mean"] == 0.110

    def test_name_max_length(self) -> None:
        with pytest.raises(ValidationError):
            TypingProfile(name="a" * 65)


class TestProfileRepository:
    def test_save_and_load(self, repo: ProfileRepository) -> None:
        p = TypingProfile(name="test_save", typo_probability=0.07)
        repo.save(p)
        loaded = repo.load("test_save")
        assert loaded.name == "test_save"
        assert loaded.typo_probability == 0.07

    def test_load_nonexistent_returns_default(self, repo: ProfileRepository) -> None:
        loaded = repo.load("nonexistent")
        assert loaded.name == "nonexistent"
        assert loaded.training_samples == 0

    def test_list_profiles_empty(self, repo: ProfileRepository) -> None:
        assert repo.list_profiles() == []

    def test_list_profiles_sorted(self, repo: ProfileRepository) -> None:
        repo.save(TypingProfile(name="zulu"))
        repo.save(TypingProfile(name="alpha"))
        repo.save(TypingProfile(name="mike"))
        assert repo.list_profiles() == ["alpha", "mike", "zulu"]

    def test_sanitizes_name(self, repo: ProfileRepository) -> None:
        p = TypingProfile(name="test@profile!")
        path = repo.save(p)
        assert path.name == "testprofile.json"
