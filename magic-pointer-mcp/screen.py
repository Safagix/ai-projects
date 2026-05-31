import io
import time
from pathlib import Path

import mss
from PIL import Image

from config import TEMP_DIR, SCREENSHOT_QUALITY, SCREENSHOT_MAX_DIM


def capture_full() -> Image.Image:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
    return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")


def capture_region(x: int, y: int, w: int, h: int) -> Image.Image:
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": w, "height": h}
        img = sct.grab(monitor)
    return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")


def get_monitors() -> list[dict]:
    with mss.mss() as sct:
        return [
            {"index": i, "top": m["top"], "left": m["left"], "width": m["width"], "height": m["height"]}
            for i, m in enumerate(sct.monitors[1:], 1)
        ]


def resize_for_vision(img: Image.Image) -> Image.Image:
    max_dim = SCREENSHOT_MAX_DIM
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    return img


def save_temp(img: Image.Image, name: str | None = None) -> Path:
    path = TEMP_DIR / f"{name or 'screenshot'}_{int(time.time())}.png"
    img.save(str(path), "PNG", optimize=True)
    return path


def img_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    import base64
    return base64.b64encode(buf.getvalue()).decode("utf-8")
