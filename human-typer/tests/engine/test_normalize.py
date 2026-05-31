from __future__ import annotations

from human_typer.engine.normalize import strip_accents


class TestStripAccents:
    def test_lowercase_acutes(self) -> None:
        assert strip_accents("\u00e1") == "a"
        assert strip_accents("\u00e9") == "e"
        assert strip_accents("\u00ed") == "i"
        assert strip_accents("\u00f3") == "o"
        assert strip_accents("\u00fa") == "u"

    def test_uppercase_acutes(self) -> None:
        assert strip_accents("\u00c1") == "A"
        assert strip_accents("\u00c9") == "E"
        assert strip_accents("\u00cd") == "I"
        assert strip_accents("\u00d3") == "O"
        assert strip_accents("\u00da") == "U"

    def test_dieresis(self) -> None:
        assert strip_accents("\u00fc") == "u"
        assert strip_accents("\u00dc") == "U"

    def test_grave(self) -> None:
        assert strip_accents("\u00e0") == "a"
        assert strip_accents("\u00c0") == "A"

    def test_circumflex(self) -> None:
        assert strip_accents("\u00e2") == "a"
        assert strip_accents("\u00ca") == "E"

    def test_tilde_preserved_lower(self) -> None:
        assert strip_accents("\u00f1") == "\u00f1"

    def test_tilde_preserved_upper(self) -> None:
        assert strip_accents("\u00d1") == "\u00d1"

    def test_preserves_maana(self) -> None:
        assert strip_accents("ma\u00f1ana") == "ma\u00f1ana"

    def test_mixed_sentence(self) -> None:
        result = strip_accents("El ni\u00f1o compr\u00f3 m\u00e1s de \u00faltil al a\u00f1o")
        assert result == "El ni\u00f1o compro mas de ultil al a\u00f1o"

    def test_no_accents_unchanged(self) -> None:
        assert strip_accents("hello world 123") == "hello world 123"

    def test_empty_string(self) -> None:
        assert strip_accents("") == ""

    def test_newlines_unchanged(self) -> None:
        assert strip_accents("a\nb") == "a\nb"

    def test_spaces_unchanged(self) -> None:
        assert strip_accents("a b") == "a b"
