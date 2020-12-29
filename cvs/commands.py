import os
import abc

from cvs import errors, config
from cvs.app import VersionsSystem

REGISTRY = {}


class CvsCommand(abc.ABC):
    def __init__(self, app: VersionsSystem):
        self._app = app

    def __init_subclass__(cls, alias=""):
        REGISTRY[alias] = cls

    @abc.abstractmethod
    def _validate(self, *args) -> None:
        pass

    @abc.abstractmethod
    def _execute(self, *args):
        pass

    def __call__(self, *args):
        self._validate(*args)
        self._execute(*args)


class InitCommand(CvsCommand, alias="init"):
    def _validate(self) -> None:
        if config.MAIN_PATH.exists():
            raise errors.RepoAlreadyExistError(os.getcwd())

    def _execute(self):
        self._app.initialize_repo()


class AddCommand(CvsCommand, alias="add"):
    def _validate(self, path_to_add: str) -> None:
        if not os.path.exists(path_to_add):
            raise errors.InvalidPathError(path_to_add)
        path_to_add = os.path.realpath(path_to_add)
        if (
            os.getcwd() != os.path.commonpath([os.getcwd(), path_to_add])
            or not config.MAIN_PATH.exists()
        ):
            raise errors.RepoNotFoundError(path_to_add)

    def _execute(self, path_to_index: str):
        self._app.add_to_staging_area(path=path_to_index)


class CommitCommand(CvsCommand, alias="commit"):
    def _validate(self, message: str) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self, message: str):
        self._app.make_commit(message)


class LogCommand(CvsCommand, alias="log"):
    def _validate(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self):
        self._app.show_logs()


class StatusCommand(CvsCommand, alias="status"):
    def _validate(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self):
        self._app.show_status()


class CheckoutCommand(CvsCommand, alias="checkout"):
    def _validate(self, commit: str) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())
        if not (config.COMMITS_PATH / commit).exists():
            errors.CommitNotFoundError(commit)

    def _execute(self, commit: str):
        self._app.checkout(commit)

