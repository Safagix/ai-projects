from __future__ import annotations

from human_typer.engine.tokenizer import Token, tokenize


class TestTokenize:
    def test_empty_string(self) -> None:
        assert tokenize("") == []

    def test_single_word(self) -> None:
        tokens = tokenize("hola")
        assert tokens == [Token(text="hola", kind="word")]

    def test_simple_sentence(self) -> None:
        tokens = tokenize("Hola mundo.")
        assert tokens == [
            Token(text="Hola", kind="word"),
            Token(text=" ", kind="space"),
            Token(text="mundo", kind="word"),
            Token(text=".", kind="punctuation", is_sentence_end=True),
        ]

    def test_multiple_spaces(self) -> None:
        tokens = tokenize("a   b")
        assert tokens == [
            Token(text="a", kind="word"),
            Token(text="   ", kind="space"),
            Token(text="b", kind="word"),
        ]

    def test_newlines(self) -> None:
        tokens = tokenize("linea1\nlinea2\n\nlinea3")
        assert tokens == [
            Token(text="linea1", kind="word"),
            Token(text="\n", kind="newline"),
            Token(text="linea2", kind="word"),
            Token(text="\n", kind="newline"),
            Token(text="\n", kind="newline"),
            Token(text="linea3", kind="word"),
        ]

    def test_exclamation_is_sentence_end(self) -> None:
        tokens = tokenize("Wow!")
        assert tokens[-1].is_sentence_end is True

    def test_question_is_sentence_end(self) -> None:
        tokens = tokenize("Que?")
        assert tokens[-1].is_sentence_end is True

    def test_comma_not_sentence_end(self) -> None:
        tokens = tokenize("Hola, mundo.")
        comma_token = tokens[1]
        assert comma_token.kind == "punctuation"
        assert comma_token.is_sentence_end is False

    def test_tabs_as_space(self) -> None:
        tokens = tokenize("a\tb")
        assert len(tokens) == 3
        assert tokens[1].kind == "space"
        assert tokens[1].text == "\t"

    def test_parentheses(self) -> None:
        tokens = tokenize("(hola)")
        kinds = [t.kind for t in tokens]
        assert kinds.count("punctuation") == 2

    def test_spanish_accents(self) -> None:
        tokens = tokenize("canción")
        assert tokens[0].text == "canción"
        assert tokens[0].kind == "word"

    def test_preserves_text_length(self) -> None:
        text = "Hola, mundo cruel!\nAdiós."
        total = sum(len(t.text) for t in tokenize(text))
        assert total == len(text)

    def test_only_punctuation(self) -> None:
        tokens = tokenize("...")
        assert len(tokens) == 1
        assert tokens[0].kind == "punctuation"

    def test_mixed_punctuation_group(self) -> None:
        tokens = tokenize("!!!")
        assert len(tokens) == 1
        assert tokens[0].text == "!!!"
