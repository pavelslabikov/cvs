import os
import abc
import zlib

from pathlib import Path
from cvs import errors, config
from cvs.models.commit import Commit
from cvs.models.index import FileIndex
from cvs.utils.factories import TreeFactory, CommitFactory
from cvs.view import BaseView


class CvsCommand(abc.ABC):
    REGISTRY = {}

    def __init__(self, view: BaseView):
        self.view = view
        self._index = None

    def __init_subclass__(cls, alias=""):
        cls.REGISTRY[alias] = cls

    @property
    def index(self):
        if not self._index:
            self._index = FileIndex(config.INDEX_PATH, config.IGNORE_PATH)
        return self._index

    @property
    def head_pointer(self):
        return config.HEAD_PATH.read_text()

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
        config.create_dirs()
        config.INDEX_PATH.write_text("")
        config.HEAD_PATH.write_text("master")
        (config.REFS_PATH / "master").write_text("root")
        self.view.display_text("Инициализирован новый репозиторий")


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
        path = os.path.relpath(path_to_index)
        if os.path.isfile(path):
            self.index.add_file(path)
        all_files = [str(x) for x in Path(path).glob("**/*") if x.is_file()]
        for file in all_files:
            self.index.add_file(file)
        self.index.refresh_file()


class CommitCommand(CvsCommand, alias="commit"):
    def _validate(self, message: str) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self, message: str):
        if self.index.is_empty:
            self.view.display_text("Нечего коммитить - индекс пуст")
            return

        root_tree = TreeFactory.create_new_tree(self.index.blobs)
        commit = CommitFactory.create_new_commit(root_tree, message)
        if commit.is_same_with_parent(config.COMMITS_PATH):
            self.view.display_text("Нечего коммитить - нет изменений")
            return

        commit.create_file(config.COMMITS_PATH)
        root_tree.create_file(config.TREES_PATH)
        if self.head_pointer == commit.parent:
            config.HEAD_PATH.write_text(commit.content_hash)
        else:
            (config.REFS_PATH / self.head_pointer).write_text(
                commit.content_hash
            )
        self.view.display_text(f"Новый коммит: {commit.content_hash}")


class LogCommand(CvsCommand, alias="log"):
    def _validate(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self):
        current_commit = self.head_pointer
        branch_file = config.REFS_PATH / current_commit
        if branch_file.exists():
            current_commit = branch_file.read_text()
        while current_commit != "root":
            path_to_commit = config.COMMITS_PATH / current_commit
            commit_content = path_to_commit.read_text()
            self.view.display_text(f"\nCommit - {current_commit}")
            self.view.display_text(f"{commit_content}\n")
            current_commit = Commit.parse_file_content(current_commit)[1]


class StatusCommand(CvsCommand, alias="status"):
    def _validate(self) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())

    def _execute(self):
        self.view.display_text(f"HEAD -> {self.head_pointer}")
        self.view.display_text("Неиндексированные файлы/изменения:\n")
        for path in Path().glob("**/*"):
            if not path.is_file():
                continue
            file = str(path)
            blob = self.index.indexed_files.get(file)
            if not blob and not self.index.is_ignored(file):
                self.view.display_text(f"new file: {file}")

            if blob and not blob.is_same_with_file(Path(file)):
                self.view.display_text(f"modified: {file}")
        self.view.display_text("\nТекущее содержимое файла индекса:")
        self.view.display_text("\n".join(self.index.indexed_files.keys()))


class CheckoutCommand(CvsCommand, alias="checkout"):
    def _validate(self, commit: str) -> None:
        if not config.MAIN_PATH.exists():
            raise errors.RepoNotFoundError(os.getcwd())
        if not (config.COMMITS_PATH / commit).exists():
            errors.CommitNotFoundError(commit)

    def _execute(self, commit: str):
        if commit == self.head_pointer:
            self.view.display_text("Вы уже на данном коммите")
        new_index = {}
        config.HEAD_PATH.write_text(commit)
        tree_hash, parent_commit = Commit.parse_file_content(commit)
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
