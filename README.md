# babble

Babble is a simple package for natural language understanding (NLU).

Babble can be used to get the *intention* from a given phrase in a
structured form. For that Babble must be configured by using a *domain
configuration*. This is a JSON file which contains all intentions and
entities within this domain:

    [
        {
            "type": "intent",
            "name": "set_timer",
            "rule": "set timer <number> <unit>"
        },
        {
            "type": "entity",
            "name": "unit",
            "rule": "minutes|minute|hours|hour"
        },
        {
            "type": "entity",
            "name": "number",
            "rule": "zero|one|two|three|four|five|six|seven|eight|((nine|niner):niner){value}"
        }
        ]

A Intention has a name and a rule. The rule is sequence of *classifiers*. A
classifier can be either a simple word or a reference to a *\<entity\>*. A entity
allows to define  more complicated rules for the classifier.

The intention recognition follows a simple rule:
Given a phrase, the intention is found when all classifiers can be
found in exact in the order as defined in rule of the intention.

Let's say we are using the domain from above and want to get the intention of
the following phrase: *set my fucking timer to nine hours*. This would be the
result:

        {
            "input": "set my fucking timer to nine hours",
            "intent": "set_timer",
            "slots": [
                {
                    "name": "set",
                    "value": "set",
                },
                {
                    "name": "timer",
                    "value": "timer"
                },
                {
                    "name": "number",
                    "value": "four",
                    "tag": "value"
                },
                {
                    "name": "unit",
                    "value": "hour"
                }
            ],
            "processed": "set timer niner hours"
        }

Awesome!

## Usage

### Cli

Use babble as cli:

        babble --domain path/to/domain.json "Hello Word"

### Lib

Use babble as lib:

        from babble.engine import Engine, Understanding
        
        engine = Engine(path_to_domain_config="/path/to/domain.json")
        understanding = engine.evaluate("Hello World")
        if understanding:
            print(understanding.as_dict())
        else:
            print("Not understood")

## Licence

Free software: MIT license

## Features

* Intent recognition
* Simple grammar for rules in entities:
  * alternatives ->  ``foo|bar|baz``
  * substitutions -> ``foo:bar``
  * tagging -> ``foo{bar}``

## Authors

* Torsten Irländer <torsten.irlaender@googlemail.com>
