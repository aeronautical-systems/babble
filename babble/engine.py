import json
import logging
from typing import Optional, Dict, List, Tuple, Union

from babble.parser import IntentTransformer, RuleTransformer, create_parser

log = logging.getLogger("babble")


class Understanding:
    """Understanding is the result of the evaluation of a phrase."""

    def __init__(self, phrase: str, intent: str, required_matched_classifiers: int):
        self.phrase: str = phrase
        """Origin phrase from which the understanding was build"""
        self.intent: str = intent
        """Intention which could be understood from the origin phrase"""
        self.slots: List[Dict[str, Union[str, List[str]]]] = []
        """Slots store informations related to the understanding of the
        phrase"""
        self.required_matched_classifiers: int = required_matched_classifiers
        """Number of required classifieres to be found"""

    def as_dict(self) -> Dict:
        return {"input": self.phrase, "intent": self.intent, "slots": self.slots}

    def add_slot(self, slot: dict):
        found = None
        for s in self.slots:
            if s["name"] == slot["name"]:
                # Add more values to the exiting slot.
                if not isinstance(s["value"], list):
                    s["value"] = [s["value"]]
                s["value"].append(slot["value"])
                break
        else:
            self.slots.append(slot)

    def is_complete(self) -> bool:
        """Returns true if we found slots at least slots"""
        count = 0
        for slot in self.slots:
            if isinstance(slot["value"], list):
                count += len(slot["value"])
            else:
                count += 1
        return count == self.required_matched_classifiers


class Engine:
    """Engine will evaluate a given phrase and tries to understand the meaning
    of the phrase based on a given domain"""

    def __init__(self, path_to_domain_config: str):
        self.domain = {}
        with open(path_to_domain_config) as f:
            self.domain = json.load(f)

        # Load intents
        self.parser = create_parser()
        self.transformer = IntentTransformer()
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

    def _expand_classifiers(
        self, classifiers: List[str], expanded_classifiers: List[str]
    ) -> List[str]:
        for classifier in classifiers:
            if is_entity(classifier):
                entity_name = get_entity_name(classifier)
                entity = self.entities[entity_name]
                rule = entity["rule"]
                if is_entity(rule):
                    tree = self.parser.parse(rule)
                    result = IntentTransformer().transform(tree)
                    return self._expand_classifiers(
                        classifiers=result, expanded_classifiers=expanded_classifiers
                    )
            expanded_classifiers.append(classifier)
        return expanded_classifiers

    def _evaluate_intent(self, intent: Dict, phrase: str) -> Optional[Understanding]:
        rule = intent.get("rule", "")
        intention = intent.get("name", "")
        log.debug("#" * 68)
        log.debug(f"{intention} -> {phrase}")
        log.debug("#" * 68)

        tree = self.parser.parse(rule)
        classifiers = IntentTransformer().transform(tree)
        expanded_classifiers = self._expand_classifiers(classifiers, [])

        understanding = Understanding(
            phrase,
            intent=intention,
            required_matched_classifiers=len(expanded_classifiers),
        )

        # Iterate of every entity in the intent
        rest_of_phrase_to_test = phrase
        for classifier in expanded_classifiers:

            # Evaluate and update the remaining phrase to test.
            slot, rest_of_phrase_to_test = self._evaluate_classifier(
                classifier, rest_of_phrase_to_test
            )

            if slot is not None:
                understanding.add_slot(slot)
                if understanding.is_complete():
                    return understanding
        return None

    def _resolve_rule_from_classifier(self, classifier: str) -> str:
        if is_entity(classifier):
            entity_name = get_entity_name(classifier)
            entity = self.entities[entity_name]
            return entity.get("rule", "")
        return classifier

    def _evaluate_classifier(
        self, classifier: str, phrase: str
    ) -> Tuple[Optional[Dict], str]:
        log.debug("*" * 68)

        rule = self._resolve_rule_from_classifier(classifier=classifier)
        tree = self.parser.parse(rule)

        words_to_test = []
        for word in phrase.split():
            words_to_test.append(word)
            phrase_to_test = " ".join(words_to_test)
            log.debug(f"{phrase_to_test} == {rule}")
            rule_transformer = RuleTransformer(phrase=phrase_to_test)
            found, tag = rule_transformer.transform(tree)
            if found:
                phrase = phrase.replace(phrase_to_test, "")
                slot = dict(name=get_entity_name(classifier), value=found)
                if tag:
                    slot["tag"] = tag
                return slot, phrase
        return None, phrase


def get_entity_name(element: str):
    return element.replace("<", "").replace(">", "")


def is_entity(element: str):
    return element.startswith("<") and element.endswith(">")
