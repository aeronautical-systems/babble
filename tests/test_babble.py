#!/usr/bin/env python

"""Tests for `babble` package."""


from click.testing import CliRunner

from babble import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
