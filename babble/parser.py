import os
from typing import List, Dict, Optional

from lark.lark import Lark
from lark.visitors import Transformer

BABBLE_PATH_GRAMMAR = os.path.join(os.getcwd(), "babble", "grammar.lark")


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


class BabbleTransformer(Transformer):
    def intent(self, toks):
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

    def intent(self, toks):
        result = []
        for tok in toks:
            result.append(tok.value)
        return [" ".join(result)]

    def start(self, toks):
        for tok in toks[0]:
            print(tok, self.phrase)
            if self.phrase.find(tok) > -1:
                return tok
        return None
