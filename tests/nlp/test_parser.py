from lark.lark import Lark
import pytest

from babble.nlp.parser import IntentTransformer, RuleTransformer, find_in_phrase


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
        ("foo|bar|baz|buz:buz", "foo", ("buz", None)),
        ("foo|bar|(baz|buz):buz", "baz", ("buz", None)),
        ("foo|bar|((baz|buz):buz)", "foo", ("foo", None)),
        ("foo|bar|(baz|buz):buz", "biz", (None, None)),
    ],
)
def test_rules(parser: Lark, rule: str, phrase: str, expected):
    tree = parser.parse(rule)
    transformer = RuleTransformer(phrase)
    result = transformer.transform(tree)
    assert result == expected


@pytest.mark.parametrize("phrase,tofind,result", [("work force", "work horse", True)])
def test_find_in_phrase(phrase, tofind, result):
    result = find_in_phrase(phrase=phrase, to_find=tofind)
    assert result is result
