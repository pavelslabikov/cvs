from cvs.app import VersionsSystem
from cvs.validator import CommandValidator
import os
from cvs.models import TreeNode
import hashlib


class CommandExecutor:
    def __init__(self):
        self._app = VersionsSystem()

    def execute_init(self):
        CommandValidator.validate_init()
        self._app.init_command()

    def execute_add(self, path: str):
        CommandValidator.validate_init()
        self._app.init_command()

    def execute_log(self):
        CommandValidator.validate_init()
        self._app.init_command()

    def execute_commit(self, message: str):
        CommandValidator.validate_init()
        self._app.init_command()
