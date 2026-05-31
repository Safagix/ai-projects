from __future__ import annotations

from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent.parent
PROFILES_DIR = ROOT_DIR / "profiles"

PROFILES_DIR.mkdir(parents=True, exist_ok=True)

MIN_TRAINING_SAMPLES = 30
SLEEP_POLL_INTERVAL = 0.05
