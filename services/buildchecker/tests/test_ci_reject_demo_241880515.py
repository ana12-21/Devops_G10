"""Verify the documented success exit code after the CI rejection demonstration."""
from buildchecker.cli import main


def test_version_returns_success_exit_code():
    assert main(["version"]) == 0
