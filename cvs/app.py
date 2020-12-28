import hashlib
import logging
import os
import zlib

from pathlib import Path
from cvs.models.index import FileIndex
from cvs.utils.factories import TreeFactory, CommitFactory
from cvs.view import BaseView
from cvs import config

logger = logging.getLogger(__name__)


class VersionsSystem:
    def __init__(self, view: BaseView):
        self._view = view
        self._current_branch = None

    def initialize_repo(self) -> None:
        config.create_dirs()
        config.INDEX_PATH.write_text("")
        config.HEAD_PATH.write_text(os.path.join(".cvs", "refs", "master"))
        self._view.display_text("Successfully initialized new repository")
        self._current_branch = config.HEAD_PATH.read_text()

    def add_to_staging_area(self, path: str) -> None:
        path = os.path.relpath(path)
        index = FileIndex(config.INDEX_PATH, config.IGNORE_PATH)
        if os.path.isfile(path):
            index.add_file(path)
        files_to_add = [str(x) for x in Path(path).glob("**/*") if x.is_file()]
        for file in files_to_add:
            index.add_file(file)
        index.refresh_file()

    def make_commit(self, message: str) -> None:
        index = FileIndex(config.INDEX_PATH, config.IGNORE_PATH)
        if index.is_empty:
            self._view.display_text("Nothing to commit - index is empty")
            return

        root_tree = TreeFactory.create_new_tree(index.blobs)
        commit = CommitFactory.create_new_commit(root_tree, message)
        if commit.is_same_with_parent(config.COMMITS_PATH):
            self._view.display_text("Nothing to commit - no changes detected")
            return

        commit.create_file(str(config.COMMITS_PATH))
        root_tree.create_file(str(config.TREES_PATH))
        current_branch = config.HEAD_PATH.read_text()
        with open(current_branch, "w") as file:
            file.write(commit.content_hash)
        self._view.display_text(f"Created new commit: {commit.content_hash}")

    def show_logs(self) -> None:
        current_branch = config.HEAD_PATH.read_text()
        branch_file = Path(current_branch)
        if not branch_file.exists():
            self._view.display_text(
                f"No commit history for branch {current_branch}"
            )
            return

        last_commit = branch_file.read_text()
        logger.debug(f"Last commit hash: {last_commit}")
        while last_commit != "root":
            logger.debug(f"Current commit hash: {last_commit}")
            path_to_commit = config.COMMITS_PATH / last_commit
            commit_content = path_to_commit.read_text()
            self._view.display_text(f"{commit_content}\n")
            last_commit = commit_content.splitlines()[1].split(" ")[1]

    def has_changes(self, file: str, blob_hash: str) -> bool:
        raw_content = Path(file).read_bytes()
        compressed = zlib.compress(raw_content)
        actual_hash = hashlib.sha1(compressed).hexdigest()
        return blob_hash != actual_hash

    def show_status(self) -> None:
        index = FileIndex(config.INDEX_PATH, config.IGNORE_PATH)
        all_files = [str(x) for x in Path().glob("**/*") if x.is_file()]
        self._view.display_text("Неиндексированные файлы/изменения:\n")
        for file in all_files:
            blob = index.indexed_files.get(file)
            if not blob and not index.is_ignored(file):
                self._view.display_text(f"not staged: {file}")

            if blob and self.has_changes(file, blob.content_hash):
                self._view.display_text(f"modified: {file}")
        self._view.display_text("\nТекущее содержимое файла индекса:")
        self._view.display_text("\n".join(index.indexed_files.keys()))

    def checkout(self, commit: str) -> None:
        commit_file = config.COMMITS_PATH / commit
        if not commit_file.exists():
            self._view.display_text(f"Не удалось найти коммит: {commit}")
        root_hash = commit_file.read_text().split("\n")[0].split(" ")[1]
        curr_tree = config.TREES_PATH / root_hash
        curr_dir = Path()



