from __future__ import annotations

import json
from pathlib import Path

from human_typer.config import PROFILES_DIR
from human_typer.profiles.models import TypingProfile


class ProfileRepository:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or PROFILES_DIR
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        sanitized = "".join(c for c in name if c.isalnum() or c in "_-")
        return self._base_dir / f"{sanitized}.json"

    def load(self, name: str) -> TypingProfile:
        path = self._path_for(name)
        if not path.exists():
            return TypingProfile(name=name)
        data = json.loads(path.read_text(encoding="utf-8"))
        return TypingProfile(**data)

    def save(self, profile: TypingProfile) -> Path:
        path = self._path_for(profile.name)
        path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return path

    def list_profiles(self) -> list[str]:
        return sorted(p.stem for p in self._base_dir.glob("*.json"))
