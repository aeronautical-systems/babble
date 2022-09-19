#!/usr/bin/env python

"""Tests for `babble` package."""


from click.testing import CliRunner

from babble.nlp import cli


def test_command_line_help():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0

def test_command_line_parse():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--domain", "tests/nlp/test.domain.json", "foo bar baz"])
    assert help_result.exit_code == 0
