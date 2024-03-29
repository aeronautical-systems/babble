import os
import re
from typing import List, Dict, Optional
import logging

from babble import PACKAGE_ROOT_DIR
from rapidfuzz.distance import Levenshtein
from lark.lark import Lark
from lark.visitors import Transformer


log = logging.getLogger("babble")
BABBLE_PATH_GRAMMAR = os.path.join(PACKAGE_ROOT_DIR, "babble", "nlp", "grammar.lark")


def create_parser() -> Lark:
    with open(BABBLE_PATH_GRAMMAR) as f:
        return Lark(f)


def dequote(string: str) -> str:
    if string.startswith("'"):
        return string.lstrip("'").rstrip("'")
    elif string.startswith('"'):
        return string.lstrip('"').rstrip('"')
    else:
        return string


# TODO adjust grammar to handle apostrophes
def remove_apostrophe(phrase: str) -> str:
    dequoted_phrase = False
    dequoted_word = False
    phrase = phrase.strip()
    if phrase.startswith("'") and phrase.endswith("'"):
        phrase = dequote(phrase)
        dequoted_phrase = True
    words = phrase.split(" ")
    phrase_as_dict = {key: "" for key in list(range(len(words)))}
    for key in phrase_as_dict.keys():
        phrase_as_dict.update({key: words[key]})

    key_list = list(phrase_as_dict.keys())
    for key in key_list:
        word = phrase_as_dict[key]
        if word.startswith("'") and word.endswith("'"):
            word = dequote(word).strip()
            dequoted_word = True
        word = word.split("'")[0]
        if dequoted_word:
            word = "'" + word + "'"
            dequoted_word = False
        phrase_as_dict.update({key: word})
    phrase = " ".join(list(phrase_as_dict.values()))
    if dequoted_phrase:
        phrase = "'" + phrase + "'"
    return phrase


def find_in_phrase(phrase: str, to_find: str) -> bool:
    """Will return True if `to_find` is found in `phrase`. The search is done
    trying a exact match first. If it does not match than a fuzzy match using
    levensthein is done"""

    # Try to get a direct match
    regex = re.compile(r"\b" + to_find + r"\b")
    if re.match(regex, phrase):
        return True  # Fine! we have a exact match

    # Ok, lets do a fuzzy match.
    words_to_test = []
    max_distance = int(len(to_find) / 5)

    # The fuzzy match is done my building the phrase in reversed order! This is
    # because the phrase might have grown with every new call:
    # foo -> foo bar -> foo bar baz
    # Now it is important to start from the end to check if we found a match to
    # ignore irrelevant parts of the phrase (e.g "foo" if we are searching for
    # "bar baz".
    for word in reversed(phrase.split()):
        words_to_test.insert(0, word)
        phrase_to_test = " ".join(words_to_test)
        d = Levenshtein.distance(phrase_to_test, to_find)
        if d <= max_distance:
            log.debug(f"{phrase_to_test} -> {to_find} with distance {d}/{max_distance}")
            return True  # Fine! We found it with some fuzzyness.
    return False  # Nothing found


class IntentTransformer(Transformer):
    def rule(self, toks):
        result = []
        for tok in toks:
            result.append(dequote(tok.value))
        return result

    def start(self, toks):
        return toks[0]


class RuleTransformer(Transformer):
    def __init__(self, phrase: str, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.phrase = phrase
        self.tag: Optional[str] = None

    def rule(self, toks):
        if find_in_phrase(self.phrase, " ".join(t for t in toks if t is not None)):
            return toks
        return None

    def subst(self, toks):
        if toks[0][0] and find_in_phrase(self.phrase, toks[0][0]):
            self.phrase = toks[1]
            return toks[1]
        return toks[0][0]

    def tagging(self, toks):
        if toks[0] is None:
            return toks[0]
        else:
            self.tag = toks[1].value
            return toks[0][0]

    def alternative(self, toks):
        for tok in toks:
            if tok is None:
                continue
            if find_in_phrase(self.phrase, tok):
                return tok
        return None

    def group(self, toks):
        return toks[0]

    def start(self, toks):
        result = toks[0]
        if result:
            return (
                " ".join(t for t in result if t is not None).strip() or None,
                self.tag,
            )
        return None, self.tag
