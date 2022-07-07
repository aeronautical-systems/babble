import os

from lark.lark import Lark
from lark.visitors import Transformer

BABBLE_PATH_GRAMMAR = os.path.join(os.getcwd(), "babble", "grammar.lark")


def create_parser() -> Lark:
    with open(BABBLE_PATH_GRAMMAR) as f:
        return Lark(f)


class BabbleTransformer(Transformer):
    def intent(self, toks):
        return " ".join([t for t in toks])

    def start(self, toks):
        return toks
