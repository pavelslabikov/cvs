from pathlib import Path
from unittest import mock
from cvs import commands, errors
from cvs.view import TestView

import pytest


@pytest.mark.parametrize("path", ["..", "../../"])
def test_adding_wrong_path(path: str):
    command = commands.AddCommand(TestView())
    try:
        command(path)
    except errors.RepoNotFoundError:
        assert True
    else:
        assert False


def test_validating_init_command():
    with mock.patch("cvs.config.MAIN_PATH", return_value=Path("tests/")):
        command = commands.InitCommand(TestView())
        try:
            command()
        except errors.RepoAlreadyExistError:
            assert True
        else:
            assert False


@pytest.mark.parametrize("path", ["___", "unknown path"])
def test_adding_non_existing_path(path: str):
    command = commands.AddCommand(TestView())
    try:
        command(path)
    except errors.InvalidPathError:
        assert True
    else:
        assert False
