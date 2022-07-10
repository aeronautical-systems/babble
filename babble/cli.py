"""Console script for babble."""
import sys
from typing import Optional
import click

from babble.engine import Engine, Understanding


@click.command()
@click.argument("phrase")
@click.option("--domain", help="Domain file with intents and rules", required=True)
def main(phrase: str, domain: str, args=None):
    """Console script for babble."""
    engine = Engine(domain)
    understanding: Optional[Understanding] = engine.evaluate(phrase)
    if understanding is not None:
        click.echo(str(understanding.as_dict()))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
