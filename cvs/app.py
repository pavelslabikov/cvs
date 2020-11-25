import hashlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from cvs.index import FileIndex
from cvs.models import TreeManager
from cvs.view import BaseView

logger = logging.getLogger(__name__)


class VersionsSystem:
    def __init__(self, view: BaseView):
        self._view = view
        self.path_to_objects = Path(".cvs/objects")
        self.path_to_index = Path(".cvs/index")
        self.path_to_head = Path(".cvs/HEAD")
        self.path_to_ignore = Path(".ignore")
        self.path_to_refs = Path(".cvs/refs")

    def initialize_context(self):
        os.mkdir(".cvs")
        if sys.platform.startswith("win32"):
            subprocess.call(['attrib', '+h', ".cvs"])
        self.path_to_refs.mkdir()
        self.path_to_objects.mkdir()
        self.path_to_index.write_text("")
        self.path_to_head.write_text(os.path.join(".cvs", "refs", "master"))

    def add_command(self, path: str):
        path = os.path.relpath(path)
        current_index = FileIndex(str(self.path_to_index))
        if os.path.isfile(path):
            current_index.add_file(path)
        files_to_add = [str(x) for x in Path(path).glob("**/*") if x.is_file()]
        for file in files_to_add:
            current_index.add_file(file)
        current_index.refresh_index_file()

    def make_commit(self, message: str):
        current_index = FileIndex(str(self.path_to_index))
        if current_index.is_empty:
            self._view.display_text("Nothing to commit")
            return
        root_tree = TreeManager.create_new_tree(current_index.blobs)
        root_hash = root_tree.get_hash()
        commit_content = f"tree {root_hash} {root_tree.name}\n" \
                         f"parent {self.get_last_commit()}\n\n" \
                         f"{message}"
        commit_hash = hashlib.sha1(commit_content.encode("utf-8")).hexdigest()
        commit_path = self.path_to_objects / commit_hash
        current_branch = self.path_to_head.read_text()
        with open(current_branch, "w") as file:
            file.write(commit_hash)
        commit_path.write_text(commit_content)
        TreeManager.create_tree_objects(root_tree)

    def log_command(self):
        with open(self.path_to_head, "r") as file:
            path_to_branch = file.read()
        logger.debug(f"Path to branch in HEAD: {path_to_branch}")
        if not os.path.exists(path_to_branch):
            print(f"No commit history for branch {path_to_branch}")
            return
        with open(path_to_branch, "r") as file:
            last_commit = file.read()
        logger.debug(f"Last commit hash: {last_commit}")
        while last_commit != "root":
            logger.debug(f"Current commit hash: {last_commit}")
            path_to_commit = os.path.join(self.path_to_objects, last_commit)
            with open(path_to_commit, "r") as file:
                commit_content = file.readlines()
                print(commit_content)
                last_commit = commit_content[1].split(" ")[1].rstrip("\n")

    def get_last_commit(self) -> str:
        path_to_branch = self.path_to_head.read_text()
        if not os.path.exists(path_to_branch):
            return "root"
        with open(path_to_branch, "r") as file:
            return file.read()
