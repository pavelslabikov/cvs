import os

from cvs import errors


class CommandValidator:
    @classmethod
    def validate_init(cls):
        if os.path.exists(".cvs"):
            raise errors.RepoAlreadyExistError(os.getcwd())

    @classmethod
    def validate_add(cls, path_to_add: str):
        if not os.path.exists(path_to_add):
            raise FileNotFoundError(path_to_add)
        path_to_add = os.path.realpath(path_to_add)
        if os.getcwd() != os.path.commonpath([os.getcwd(), path_to_add]) or not os.path.exists(".cvs"):
            raise errors.RepoNotFoundError(path_to_add)

    @classmethod
    def validate_log(cls):
        if not os.path.exists(".cvs"):
            raise errors.RepoNotFoundError(os.getcwd())

    @classmethod
    def validate_commit(cls):
        if not os.path.exists(".cvs"):
            raise errors.RepoNotFoundError(os.getcwd())