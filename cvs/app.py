import hashlib
import logging
import os
import zlib

from pathlib import Path
from cvs.models.commit import Commit
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
        config.HEAD_PATH.write_text("master")
        (config.REFS_PATH / "master").write_text("root")
        self._view.display_text("Инициализирован новый репозиторий")
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
            self._view.display_text("Нечего коммитить - индекс пуст")
            return

        root_tree = TreeFactory.create_new_tree(index.blobs)
        commit = CommitFactory.create_new_commit(root_tree, message)
        if commit.is_same_with_parent(config.COMMITS_PATH):
            self._view.display_text("Нечего коммитить - нет изменений")
            return

        commit.create_file(str(config.COMMITS_PATH))
        root_tree.create_file(str(config.TREES_PATH))
        current_branch = config.HEAD_PATH.read_text()
        if current_branch == commit.parent:
            config.HEAD_PATH.write_text(commit.content_hash)
        else:
            (config.REFS_PATH / current_branch).write_text(commit.content_hash)
        self._view.display_text(f"Новый коммит: {commit.content_hash}")

    def show_logs(self) -> None:
        current_commit = config.HEAD_PATH.read_text()
        branch_file = config.REFS_PATH / current_commit
        if branch_file.exists():
            current_commit = branch_file.read_text()
        logger.debug(f"Last commit hash: {current_commit}")
        while current_commit != "root":
            logger.debug(f"Current commit hash: {current_commit}")
            path_to_commit = config.COMMITS_PATH / current_commit
            commit_content = path_to_commit.read_text()
            self._view.display_text(f"\nCommit - {current_commit}")
            self._view.display_text(f"{commit_content}\n")
            current_commit = commit_content.splitlines()[1].split(" ")[1]

    def has_changes(self, file: str, blob_hash: str) -> bool:
        raw_content = Path(file).read_bytes()
        compressed = zlib.compress(raw_content)
        actual_hash = hashlib.sha1(compressed).hexdigest()
        return blob_hash != actual_hash

    def show_status(self) -> None:
        self._view.display_text(f"HEAD -> {config.HEAD_PATH.read_text()}")
        index = FileIndex(config.INDEX_PATH, config.IGNORE_PATH)
        all_files = [str(x) for x in Path().glob("**/*") if x.is_file()]
        self._view.display_text("Неиндексированные файлы/изменения:\n")
        for file in all_files:
            blob = index.indexed_files.get(file)
            if not blob and not index.is_ignored(file):
                self._view.display_text(f"new file: {file}")

            if blob and self.has_changes(file, blob.content_hash):
                self._view.display_text(f"modified: {file}")
        self._view.display_text("\nТекущее содержимое файла индекса:")
        self._view.display_text("\n".join(index.indexed_files.keys()))

    def checkout_commit(self, commit: str) -> None:
        if commit == config.HEAD_PATH.read_text():
            self._view.display_text("Вы уже на данном коммите")
        new_index = {}
        config.HEAD_PATH.write_text(commit)
        tree_hash, parent_commit = Commit.parse_file_content(commit)  # TODO: fix
        self.traverse_tree(tree_hash, Path(), new_index)
        content_to_write = []
        for file in sorted(new_index.keys()):
            content_to_write.append(f"{file} {new_index[file]}")
        config.INDEX_PATH.write_text("\n".join(content_to_write))

    def traverse_tree(self, tree_hash: str, curr_dir: Path, new_index: dict):
        curr_tree = config.TREES_PATH / tree_hash
        tree_content = curr_tree.read_text().split("\n")
        for line in tree_content:
            obj_type, hashcode, filename = line.split(" ")
            if obj_type == "blob":
                new_index[filename] = hashcode
                blob_content = (config.BLOBS_PATH / hashcode).read_bytes()
                path = curr_dir / filename
                path.write_bytes(zlib.decompress(blob_content))
            else:
                self.traverse_tree(hashcode, curr_dir / filename, new_index)



