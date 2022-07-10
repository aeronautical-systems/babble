"""Console script for babble."""
import sys
import logging
from typing import Optional
import click

from babble.engine import Engine, Understanding

logging.basicConfig()
log = logging.getLogger("babble")


@click.command()
@click.argument("phrase")
@click.option("--domain", help="Domain file with intents and rules", required=True)
@click.option("-v", "--verbose", count=True)
def main(phrase: str, domain: str, verbose: int, args=None):
    """Console script for babble."""

    # Setup logging
    if verbose == 1:
        log.setLevel(logging.INFO)
    if verbose > 1:
        log.setLevel(logging.DEBUG)

    engine = Engine(domain)
    understanding: Optional[Understanding] = engine.evaluate(phrase)
    if understanding is not None:
        click.echo(str(understanding.as_dict()))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
