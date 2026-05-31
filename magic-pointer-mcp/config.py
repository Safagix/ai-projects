import os
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    for candidate in [Path(path), Path(__file__).parent / ".env"]:
        if candidate.exists():
            for raw in candidate.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
            return


_load_dotenv()


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
VISION_MODEL = os.getenv("VISION_MODEL", "moondream:latest")

MAGIC_MODE = os.getenv("MAGIC_MODE", "auto").lower()
if MAGIC_MODE not in ("auto", "guided"):
    MAGIC_MODE = "auto"

CLICK_PAUSE = float(os.getenv("CLICK_PAUSE", "0.3"))
TYPE_INTERVAL_MIN = float(os.getenv("TYPE_INTERVAL_MIN", "0.03"))
TYPE_INTERVAL_MAX = float(os.getenv("TYPE_INTERVAL_MAX", "0.08"))
MOVE_DURATION = float(os.getenv("MOVE_DURATION", "0.3"))

SCREENSHOT_QUALITY = int(os.getenv("SCREENSHOT_QUALITY", "85"))
SCREENSHOT_MAX_DIM = int(os.getenv("SCREENSHOT_MAX_DIM", "1920"))

SAFETY_MARGIN_PX = int(os.getenv("SAFETY_MARGIN_PX", "10"))

TEMP_DIR = Path(os.getenv("TEMP", Path.home() / "AppData" / "Local" / "Temp")) / "magic_pointer"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
