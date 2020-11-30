import os
import abc
from cvs import errors, config
from cvs.app import VersionsSystem


class CvsCommand(abc.ABC):
    def __init__(self, app: VersionsSystem, *args):
        self._app = app
        self._args = args

    @abc.abstractmethod
    def _validate_args(self) -> None:
        pass

    @abc.abstractmethod
    def _execute(self, *args):
        pass

    def execute(self):
        self._validate_args()
        self._execute(*self._args)


class InitCommand(CvsCommand):
    def _validate_args(self) -> None:
        if config.MAIN_PATH.exists():
            raise errors.RepoAlreadyExistError(os.getcwd())

    def _execute(self):
        self._app.initialize_repo()


class AddCommand(CvsCommand):
    def _validate_args(self) -> None:
        path_to_add, = self._args
        if not os.path.exists(path_to_add):
            raise errors.InvalidPathError(path_to_add)
        path_to_add = os.path.realpath(path_to_add)
        if os.getcwd() != os.path.commonpath([os.getcwd(), path_to_add]) or \
                not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(path_to_add)

    def _execute(self, path_to_index: str):
        self._app.add_to_staging_area(path=path_to_index)


class CommitCommand(CvsCommand):
    def _validate_args(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self, message: str):
        self._app.make_commit(message)


class LogCommand(CvsCommand):
    def _validate_args(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self):
        self._app.show_logs()
