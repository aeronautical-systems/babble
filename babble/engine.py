import json
from typing import Optional, Dict, List, Tuple

from babble.parser import BabbleTransformer, create_parser


class Understanding:
    """Understanding is the result of the evaluation of a phrase."""

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
        self.entities: Dict[str, Dict] = self._load_entities()

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

    def _load_entities(self) -> Dict[str, Dict]:
        entities = {}
        for element in self.domain:
            if element.get("type") == "entity":
                entities[element.get("name")] = element
        return entities

    def evaluate(self, phrase: str) -> Optional[Understanding]:
        """Returns the Understanding of the given phrase. If phrase could not
        be understood None is returnd"""

        # Try to match the given phrase with all intents. As soon as a matching
        # intent is found return it.
        for intent in self.intents:
            understanding = self._evaluate_intent(intent, phrase)
            if understanding is not None:
                return understanding
        return None

    def _evaluate_intent(self, intent: Dict, phrase: str) -> Optional[Understanding]:
        rule = intent.get("rule", "")
        intention = intent.get("name", "")
        print("#" * 68)
        print(f"{intention} -> {phrase}")
        print("#" * 68)
        understanding = Understanding(phrase, intent=intention)
        slots = []

        tree = self.parser.parse(rule)
        classifieres = BabbleTransformer().transform(tree)
        required_matches = len(classifieres)

        # Iterate of every entity in the intent
        rest_of_phrase_to_test = phrase
        for classifier in classifieres:

            # Evaluate and update the remaining phrase to test.
            slot, rest_of_phrase_to_test = self._evaluate_classifier(
                classifier, rest_of_phrase_to_test
            )

            # TODO: Added slots directly to understanding and ask understanding
            # of it is complete.
            if slot is not None:
                slots.append(slot)
                # If we found all classifieres than we
                if len(slots) == required_matches:
                    return understanding
        return None

    def _evaluate_classifier(
        self, classifier: str, phrase: str
    ) -> Tuple[Optional[Dict], str]:
        print("*" * 68)

        # TODO: Implement for reference to other entities
        if is_entity(classifier):
            entity_name = get_entity_name(classifier)
            entity = self.entities[entity_name]
            rule = entity.get("rule", "")
        else:
            # The rule is simple: just the element
            rule = classifier

        # tree = self.parser.parse(rule)

        words_to_test = []
        for word in phrase.split():
            words_to_test.append(word)
            phrase_to_test = " ".join(words_to_test)
            print(f"{phrase_to_test} == {rule}")
            # TODO: User transformer to evalute this
            # TODO: Is find correct or do we need optionals here?
            if phrase_to_test.find(rule) > -1:
                phrase = phrase.replace(phrase_to_test, "")
                return {}, phrase
        return None, phrase


def get_entity_name(element: str):
    return element.replace("<", "").replace(">", "")


def is_entity(element: str):
    return element.startswith("<") and element.endswith(">")
