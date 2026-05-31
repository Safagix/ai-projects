from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from human_typer.ai.client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    check_ollama_health,
    query_ollama,
)


class TestQueryOllama:
    def test_returns_content(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"message": {"content": "texto procesado"}}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = query_ollama("hola mundo")
            assert result == "texto procesado"

    def test_passes_correct_model(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"message": {"content": "ok"}}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = mock_response
            query_ollama("texto", model="qwen2.5-coder:1.5b")
            call_args = mock_open.call_args[0][0]
            body = json.loads(call_args.data.decode("utf-8"))
            assert body["model"] == "qwen2.5-coder:1.5b"

    def test_connection_error(self) -> None:
        from urllib.error import URLError

        with patch("urllib.request.urlopen", side_effect=URLError("refused")):
            with pytest.raises(ConnectionError, match="Ollama no disponible"):
                query_ollama("texto")

    def test_empty_response(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"message": {"content": ""}}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            with pytest.raises(ValueError, match="vac\u00edo"):
                query_ollama("texto")

    def test_error_in_payload(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"error": "model not found"}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            with pytest.raises(ValueError, match="model not found"):
                query_ollama("texto")

    def test_strips_content(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"message": {"content": "  processed text  "}}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = query_ollama("raw")
            assert result == "processed text"


class TestCheckOllamaHealth:
    def test_healthy(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"models": [{"name": "llama3.2:1b"}]}
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            assert check_ollama_health() is True

    def test_unhealthy(self) -> None:
        with patch("urllib.request.urlopen", side_effect=OSError):
            assert check_ollama_health() is False

    def test_invalid_json(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            assert check_ollama_health() is False


class TestAiModuleIdle:
    def test_ai_module_not_loaded_at_startup(self) -> None:
        import subprocess
        import sys

        script = "import sys; assert 'human_typer.ai' not in sys.modules; print('idle OK')"
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=10,
        )
        assert "idle OK" in result.stdout, f"stdout={result.stdout} stderr={result.stderr}"
