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
        ("word", "word", ("word", None)),
        ("foo bar", "bar", (None, None)),
        ("foo bar", "foo bar", ("foo bar", None)),
        ("bar", "foo bar", ("bar", None)),
        ("foo|bar", "bar", ("bar", None)),
        ("foo|bar", "foo", ("foo", None)),
        ("(foo|bar)", "foo", ("foo", None)),
        ("(foo|bar)", "baz", (None, None)),
        ("foo:bar", "foo", ("bar", None)),
        ("(foo|bar):baz", "foo", ("baz", None)),
        ("(foo|bar):baz", "fuu", (None, None)),
        ("(foo|bar):baz{xxx}", "fuu", (None, "xxx")),
        ("(foo|bar):baz{xxx}", "bar", ("baz", "xxx")),
    ],
)
def test_rules(parser: Lark, rule: str, phrase: str, expected):
    tree = parser.parse(rule)
    transformer = RuleTransformer(phrase)
    result = transformer.transform(tree)
    assert result == expected
