import json
from typing import Optional, Dict, List

from babble.parser import BabbleTransformer, create_parser


class Understanding:
    """Understanding is the the result of the evaluation of a phrase."""

    def __init__(self, phrase: str, intent: str):
        self.phrase: str = phrase
        """Origin phrase from which the understanding was build"""
        self.intent: str = intent
        """Intention which could be understood from the origin phrase"""


class Engine:
    """Engine will evaluate a given phrase and tries to understand the meaning
    of the phrase based on a given domain"""

    def __init__(self, path_to_domain_config: str):
        self.domain = {}
        with open(path_to_domain_config) as f:
            self.domain = json.load(f)

        # Load intents
        self.parser = create_parser()
        self.transformer = BabbleTransformer()
        self.intents: List[Dict] = self._load_intents()

    def _load_intents(self) -> List[Dict]:
        def get_number_entities(rule: str) -> int:
            words = rule.replace("<", "").replace(">", "")
            return len(words.split())

        intents: List[Dict] = []
        for element in self.domain:
            if element.get("type") == "intent":
                intents.append(element)
        return sorted(
            intents, key=lambda x: get_number_entities(x.get("rule", "")), reverse=True
        )

    def evaluate(self, phrase: str) -> Optional[Understanding]:
        """Returns the Understanding of the given phrase. If phrase could not
        be understood None is returnd"""
        for intent in self.intents:

            rule = intent.get("rule", "")
            intention = intent.get("name", "")
            tree = self.parser.parse(rule)
            result = self.transformer.transform(tree)

            if result[0] == phrase:
                return Understanding(phrase, intent=intention)

        return None
