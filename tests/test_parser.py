from lark.lark import Lark
import pytest

from babble.parser import BabbleTransformer


@pytest.mark.parametrize(
    "phrase,expected",
    [
        ("word", ["word"]),
        ("word word", ["word", "word"]),
        ("'word' word", ["word", "word"]),
        ("'word123' word", ["word123", "word"]),
        ("'word123' word word", ["word123", "word", "word"]),
        ("'word word' word", ["word word", "word"]),
    ],
)
def test_terminals(parser: Lark, transformer: BabbleTransformer, phrase: str, expected):
    tree = parser.parse(phrase)
    result = transformer.transform(tree)
    assert result == expected
