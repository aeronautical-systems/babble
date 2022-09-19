import pytest

from babble.nlp.engine import Engine, Understanding


def test_intents_are_sorted(engine: Engine):

    last_len_intent = 1000
    for intent in engine.intents:
        assert len(intent) <= last_len_intent
        last_len_intent = len(intent)


@pytest.mark.parametrize(
    "phrase,understood,intent",
    [
        ("foo", True, "my_foo_intent"),
        ("foo bar", True, "my_foo_bar_intent"),
        ("foo bar baz", True, "my_foo_bar_baz_intent"),
        ("foo bar xxx", True, "my_foo_bar_intent"),
        ("xxx foo bar baz", True, "my_xxx_foo_bar_baz_intent"),
        ("zzz foo bar baz", True, "my_foo_bar_baz_intent"),
        ("zzz foo baz bar", True, "my_foo_bar_intent"),
        ("zzz baz bar zzz", False, ""),
    ],
)
def test_evaluate_intent(engine: Engine, phrase, understood, intent):
    result = engine.evaluate(phrase)
    if understood:
        assert isinstance(result, Understanding), "Failed to understand"
        assert result.intent == intent, "Found wrong intent"
        assert len(result.slots) != 0
    else:
        if result:
            err = f"Supprised to find intent: {result.intent}"
            assert result is None, err
        assert result is None


def test_multi_number(engine: Engine):
    result = engine.evaluate("foo one two three")
    assert result is not None
    assert result.intent == "my_foo_multi_number"
    assert result.slots[1]["value"] == ["one", "two", "three"]
