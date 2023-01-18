import json
import os
import logging
import time
from typing import Optional, Dict, List, Tuple, Union

from babble.nlp.parser import IntentTransformer, RuleTransformer, create_parser

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

    def __str__(self):
        return str(self.as_dict())

    def as_dict(self) -> Dict:
        result = {"input": self.phrase, "intent": self.intent, "slots": self.slots}

        processed = []
        for slot in self.slots:
            value = slot["value"]
            if isinstance(value, list):  # pragma: no cover
                value = " ".join(value)
            processed.append(value)
        result["processed"] = " ".join(processed)
        return result

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

    def validity(self) -> float:
        num_words = len(self.phrase.split())
        num_matches = 0
        for slot in self.slots:
            if isinstance(slot["value"], list):
                num_matches += len(slot["value"])
            else:
                num_matches += 1
        return num_matches / num_words

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
        self.domain = []
        with open(path_to_domain_config) as f:
            basedir = os.path.dirname(path_to_domain_config)
            config = json.load(f)
            if "includes" in config:
                for path in config["includes"]:
                    with open(os.path.join(basedir, path)) as i:
                        self.domain.extend(json.load(i))
            else:
                self.domain = config

        # Do some preloading of intents with classifiers and prebuild parse
        # trees for rules.
        self.parser = create_parser()
        self.transformer = IntentTransformer()
        self.entities: Dict[str, Dict] = self._load_entities()
        self.intents: List[Dict] = self._load_intents()
        self.classifiers_rule_trees: Dict = self._load_classifier_rule_trees()

    def _load_classifier_rule_trees(self) -> Dict:
        rules = {}
        for intent in self.intents:
            for classifier in intent.get("classifiers", []):
                if classifier in rules:
                    continue
                rule = self._resolve_rule_from_classifier(classifier=classifier)
                tree = self.parser.parse(rule)
                rules[classifier] = tree
        return rules

    def _load_intents(self) -> List[Dict]:
        def get_number_entities(rule: str) -> int:
            words = rule.replace("<", "").replace(">", "")
            return len(words.split())

        intents: List[Dict] = []
        for element in self.domain:
            if element.get("type") == "intent":
                rule = element.get("rule", "")
                tree = self.parser.parse(rule)
                classifiers = IntentTransformer().transform(tree)
                element["classifiers"] = self._expand_classifiers(classifiers, [])
                element.update({"len_rule": len(element["rule"].split(" "))})
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

    def _get_best_match(self, alternatives: List[Understanding]):
        alternatives_len = {
            alternative: alternative.required_matched_classifiers
            for alternative in alternatives
        }
        max_len = max(alternatives_len.values())
        longest_alternatives = [
            key for key in alternatives_len.keys() if alternatives_len[key] == max_len
        ]
        if len(longest_alternatives) == 1:
            return longest_alternatives[0]
        else:
            alternatives_validity = {
                alternative: alternative.validity()
                for alternative in longest_alternatives
            }
            log.info(
                f"Alternative intents{[(alternative.intent, alternative.validity()) for alternative in alternatives_validity]}"
            )
            alternative = max(alternatives_validity, key=alternatives_validity.get)
            return alternative

    def evaluate(self, phrase: str) -> Optional[Understanding]:
        """Returns the Understanding of the given phrase. If phrase could not
        be understood None is returnd"""

        # Try to match the given phrase with intents.
        #
        # For performance improvements intents are filtered based on rule length
        # so that rules of intent matches nearly the length of the phrase.
        # Rules which are too long or short might match, but are not taken into
        # account anyway because of the validity calculation of the match.

        alternatives = []
        start = time.perf_counter()
        intents_to_test = self._filter_intents_by_lenght(phrase)
        for intent in intents_to_test:
            understanding = self._evaluate_intent(intent, phrase)
            if understanding is not None:
                alternatives.append(understanding)

        if alternatives:
            understanding = self._get_best_match(alternatives)
            stop = time.perf_counter()
            log.info(
                f"Evaluated {len(self.intents)} intents in {stop - start:0.4f} seconds"
            )
            return understanding
        stop = time.perf_counter()
        log.info(
            f"Evaluated {len(self.intents)} intents in {stop - start:0.4f} seconds"
        )
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
        intention = intent.get("name", "")
        log.debug("#" * 68)
        log.debug(f"{intention} -> {phrase}")
        log.debug("#" * 68)

        classifiers = intent.get("classifiers", [])

        understanding = Understanding(
            phrase,
            intent=intention,
            required_matched_classifiers=len(classifiers),
        )

        # Iterate of every entity in the intent
        rest_of_phrase_to_test = phrase
        for classifier in classifiers:

            # Evaluate and update the remaining phrase to test.
            slot, rest_of_phrase_to_test = self._evaluate_classifier(
                classifier, rest_of_phrase_to_test
            )

            if slot is not None:
                understanding.add_slot(slot)
                validity = understanding.validity()
                log.debug(f"Validity: {validity}")
                if understanding.is_complete() and validity >= 0.3:
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

        tree = self.classifiers_rule_trees[classifier]

        words_to_test = []
        for word in phrase.split():
            words_to_test.append(word)
            phrase_to_test = " ".join(words_to_test)
            log.debug(f"{phrase_to_test} == {classifier}")
            rule_transformer = RuleTransformer(phrase=phrase_to_test)
            found, tag = rule_transformer.transform(tree)
            if found:
                phrase = phrase.replace(phrase_to_test, "", 1)
                slot = dict(name=get_entity_name(classifier), value=found)
                if tag:
                    slot["tag"] = tag
                return slot, phrase
        return None, phrase

    def _filter_intents_by_lenght(self, phrase: str) -> List[Dict]:
        phrase_len = len(phrase.split(" "))
        min_lim, max_lim = (phrase_len - 3, phrase_len + 3)
        intents_to_test = [
            intent for intent in self.intents if min_lim < intent["len_rule"] < max_lim
        ]
        return intents_to_test


def get_entity_name(element: str):
    return element.replace("<", "").replace(">", "")


def is_entity(element: str):
    return element.startswith("<") and element.endswith(">")
