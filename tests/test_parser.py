from lark.lark import Lark
import pytest

from babble.parser import IntentTransformer, RuleTransformer


@pytest.mark.parametrize(
    "phrase,expected",
    [
        ("word", ["word"]),
        ("word word", ["word", "word"]),
        ('"word" word', ["word", "word"]),
        ("'word123' word", ["word123", "word"]),
        ("'word123' word word", ["word123", "word", "word"]),
        ("'word word' word", ["word word", "word"]),
        ("'word word' word", ["word word", "word"]),
    ],
)
def test_terminals(parser: Lark, transformer: IntentTransformer, phrase: str, expected):
    tree = parser.parse(phrase)
    result = transformer.transform(tree)
    assert result == expected


@pytest.mark.parametrize(
    "rule, phrase, expected",
    [
        ("word", "word", "word"),
        ("foo bar", "bar", None),
        ("foo bar", "foo bar", "foo bar"),
        ("bar", "foo bar", "bar"),
        ("foo|bar", "bar", "bar"),
        ("foo|bar", "foo", "foo"),
        ("(foo|bar)", "foo", "foo"),
        ("(foo|bar)", "baz", None),
        ("foo:bar", "foo", "bar"),
        ("(foo|bar):baz", "foo", "baz"),
        ("(foo|bar):baz", "fuu", None),
    ],
)
def test_rules(parser: Lark, rule: str, phrase: str, expected):
    tree = parser.parse(rule)
    transformer = RuleTransformer(phrase)
    result = transformer.transform(tree)
    assert result == expected
