import json
from typing import Any

import httpx

from config import OLLAMA_BASE_URL, VISION_MODEL


class VisionClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self.model = model or VISION_MODEL

    def _chat(self, prompt: str, image_base64: str | None = None, temperature: float = 0.1) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 300},
        }
        if image_base64:
            payload["images"] = [image_base64]

        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()

    def describe(self, image_base64: str) -> str:
        return self._chat(
            "Describe every UI element visible on this screenshot in detail. List buttons, text fields, menus, icons, and their approximate positions. Be concise but thorough.",
            image_base64,
        )

    def ask(self, image_base64: str, question: str) -> str:
        return self._chat(question, image_base64)

    def find_element(self, image_base64: str, description: str) -> dict:
        prompt = (
            f"Find the UI element described as: '{description}'. "
            f"Return ONLY a JSON object with keys: x, y, confidence (0-100), label. "
            f"Example: {{\"x\": 450, \"y\": 300, \"confidence\": 90, \"label\": \"Submit button\"}} "
            f"Do not add any explanation, only the JSON."
        )
        raw = self._chat(prompt, image_base64, temperature=0.0)
        raw = raw.strip().strip("```").strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()
        try:
            result = json.loads(raw)
            return {
                "x": int(result.get("x", 0)),
                "y": int(result.get("y", 0)),
                "confidence": int(result.get("confidence", 0)),
                "label": str(result.get("label", description)),
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            return {"x": 0, "y": 0, "confidence": 0, "label": description, "raw": raw}

    def health(self) -> dict:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=10.0)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            has_vision = self.model in models
            return {"status": "ok", "models": models, "vision_model_available": has_vision}
        except Exception as e:
            return {"status": "error", "error": str(e)}
