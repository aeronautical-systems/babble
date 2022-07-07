import pytest
from lark.lark import Lark

from babble.parser import create_parser, BabbleTransformer


@pytest.fixture
def parser() -> Lark:
    return create_parser()


@pytest.fixture
def transformer() -> BabbleTransformer:
    return BabbleTransformer()
