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
        if self.phrase.find(" ".join(t for t in toks if t is not None)) > -1:
            return toks
        return None

    def subst(self, toks):
        if toks[0][0] and self.phrase.find(toks[0][0]) > -1:
            self.phrase = toks[1]
            return toks[1]
        return toks[0][0]

    def tagging(self, toks):
        self.tag = toks[1]
        return toks[0][0]

    def alternative(self, toks):
        for tok in toks:
            if self.phrase.find(tok) > -1:
                return tok
        return None

    def group(self, toks):
        return toks[0]

    def start(self, toks):
        result = toks[0]
        if result:
            return " ".join(t for t in result if t is not None).strip() or None, self.tag
        return None, self.tag
