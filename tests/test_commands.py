import pytest

from pathlib import Path
from unittest import mock
from cvs import commands, errors


@pytest.mark.parametrize("path", ["..", "../../"])
def test_adding_wrong_path(path: str, test_view):
    command = commands.AddCommand(test_view)
    try:
        command(path)
    except errors.RepoNotFoundError:
        assert True
    else:
        assert False


@pytest.mark.parametrize("path", ["___", "unknown path"])
def test_adding_non_existing_path(path: str, test_view):
    command = commands.AddCommand(test_view)
    try:
        command(path)
    except errors.InvalidPathError:
        assert True
    else:
        assert False


def test_validating_init_command(test_view):
    with mock.patch("cvs.config.MAIN_PATH", return_value=Path("tests/")):
        command = commands.InitCommand(test_view)
        try:
            command()
        except errors.RepoAlreadyExistError:
            assert True
        else:
            assert False


def test_init_command(test_view, test_dir):
    commands.InitCommand(test_view)()
    assert Path(".cvs").exists()
    assert test_view.buffer[0].startswith("Инициализирован")


def test_commit_output(test_view, test_dir):
    commands.InitCommand(test_view)()
    commands.CommitCommand(test_view)("test")
    assert test_view.buffer[1].startswith("Нечего коммитить")


def test_log_output(test_view, test_dir):
    commands.InitCommand(test_view)()
    commands.LogCommand(test_view)()
    assert len(test_view.buffer) == 1


def test_status_command(test_view, test_dir):
    commands.InitCommand(test_view)()
    command = commands.StatusCommand(test_view)
    command()
    assert test_view.buffer[1].startswith("HEAD")
