import pytest
import os
from lark.lark import Lark

from babble.parser import create_parser, IntentTransformer
from babble.engine import Engine


@pytest.fixture
def parser() -> Lark:
    return create_parser()


@pytest.fixture
def transformer() -> IntentTransformer:
    return IntentTransformer()


@pytest.fixture
def engine() -> Engine:
    path = os.path.join(os.getcwd(), "tests", "test.domain.json")
    return Engine(path_to_domain_config=path)
