from pathlib import Path
from unittest import mock
from cvs import commands, errors

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "..", "../../"
    ]
)
def test_adding_wrong_path(testing_app, path: str):
    command = commands.AddCommand(testing_app, path)
    try:
        command.execute()
    except errors.RepoNotFoundError:
        assert True
    else:
        assert False


def test_validating_init_command(testing_app):
    with mock.patch("cvs.config.MAIN_PATH", return_value=Path("tests/")):
        command = commands.InitCommand(testing_app)
        try:
            command.execute()
        except errors.RepoAlreadyExistError:
            assert True
        else:
            assert False


@pytest.mark.parametrize(
    "path",
    [
        "___"
    ]
)
def test_adding_non_existing_path(testing_app, path: str):
    command = commands.AddCommand(testing_app, path)
    try:
        command.execute()
    except errors.InvalidPathError:
        assert True
    else:
        assert False
