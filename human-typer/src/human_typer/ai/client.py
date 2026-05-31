from __future__ import annotations

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "deepseek-r1:1.5b"
DEFAULT_TIMEOUT = 120

_SYSTEM_PROMPT = (
    "Eres un procesador de texto para un simulador de escritura humana. "
    "Lee el siguiente texto y devuelvelo exactamente igual, sin a\u00f1adir ni "
    "quitar nada. Solo corrige errores tipograficos obvios y normaliza "
    "espaciado si es necesario. No incluyas explicaciones ni comentarios. "
    "Responde UNICAMENTE con el texto procesado."
)


def query_ollama(
    text: str,
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    temperature: float = 0.3,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    import json
    import urllib.error
    import urllib.request

    url = f"{base_url.rstrip('/')}/api/chat"

    body = {
        "model": model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"TEXTO A PROCESAR:\n---\n{text}\n---"},
        ],
    }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, TimeoutError):
            raise ConnectionError(
                f"El modelo tard\u00f3 demasiado (> {timeout}s). "
                "Prueba con un texto m\u00e1s corto."
            ) from exc
        raise ConnectionError(
            f"Ollama no disponible en {base_url}. Verifica: ollama serve"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Respuesta inv\u00e1lida del servidor Ollama") from exc

    if "error" in payload:
        raise ValueError(payload["error"])

    message = payload.get("message")
    if message is None:
        raise ValueError("El modelo no devolvi\u00f3 contenido en la respuesta")

    content = message.get("content", "").strip()
    if not content:
        raise ValueError("El modelo devolvi\u00f3 texto vac\u00edo")

    return content


def check_ollama_health(base_url: str = DEFAULT_BASE_URL, timeout: int = 5) -> bool:
    import json
    import urllib.error
    import urllib.request

    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False
    return "models" in payload
