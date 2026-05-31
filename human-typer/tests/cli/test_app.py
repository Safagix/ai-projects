from __future__ import annotations

from typer.testing import CliRunner

from human_typer.cli.app import app

runner = CliRunner()


class TestCLIHelp:
    def test_no_args_shows_help(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code != 0
        assert "Usage" in result.stdout or "Commands" in result.stdout

    def test_profiles_list(self) -> None:
        result = runner.invoke(app, ["profiles", "list"])
        assert result.exit_code == 0

    def test_type_requires_text(self) -> None:
        result = runner.invoke(app, ["type-text"])
        assert result.exit_code != 0

    def test_type_with_file_missing(self) -> None:
        result = runner.invoke(app, ["type-text", "--file", "nonexistent.txt"])
        assert result.exit_code != 0

    def test_train_help(self) -> None:
        result = runner.invoke(app, ["train", "--help"])
        assert result.exit_code == 0
        assert "--profile" in result.stdout


class TestSpeedOption:
    def test_speed_in_help(self) -> None:
        result = runner.invoke(app, ["type-text", "--help"])
        assert result.exit_code == 0
        assert "--speed" in result.stdout

    def test_speed_out_of_range_low(self) -> None:
        result = runner.invoke(app, ["type-text", "hola", "--speed", "0.0"])
        assert result.exit_code != 0

    def test_speed_out_of_range_high(self) -> None:
        result = runner.invoke(app, ["type-text", "hola", "--speed", "10.0"])
        assert result.exit_code != 0


class TestAiOption:
    def test_ai_flag_in_help(self) -> None:
        result = runner.invoke(app, ["type-text", "--help"])
        assert result.exit_code == 0
        assert "--ai" in result.stdout

    def test_ai_without_file(self) -> None:
        result = runner.invoke(app, ["type-text", "--ai", "hello"])
        assert result.exit_code != 0
