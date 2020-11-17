import os
import ctypes
import sys
import hashlib
import zlib
import glob
import logging
from cvs.models import TreeNode
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class VersionsSystem:
    root: TreeNode

    def __init__(self):
        self.path_to_objects = os.path.join(".cvs", "objects")
        self.path_to_index = os.path.join(".cvs", "index")
        self.path_to_head = os.path.join(".cvs", "HEAD")
        self.path_to_ignore = ".ignore"
        self.path_to_refs = os.path.join(".cvs", "refs")
        self.indexed_files = self.get_indexed_files()
        self.ignored_files = self.get_ignored_files()

    @property
    def is_init(self) -> bool:
        return Path(".cvs").exists()

    def init_command(self):
        os.mkdir(".cvs")
        os.mkdir(self.path_to_refs)
        os.mkdir(self.path_to_objects)
        with open(self.path_to_index, "w"):
            pass
        with open(self.path_to_head, "w") as file:
            file.write(os.path.join(".cvs", "refs", "master"))

    def get_indexed_files(self) -> dict:
        """Получение списка всех индексированных файлов"""
        if not self.is_init:
            return {}
        result = {}
        with open(self.path_to_index, "r") as index:
            for line in index.readlines():
                logger.debug(f'Current indexed file: {line}')
                path, content_hash = line.rstrip("\n").split(" ")
                result[path] = content_hash
        return result

    def add_command(self, path: str):
        path_to_crawl = os.path.join(path, "**")
        for line in glob.glob(path_to_crawl, recursive=True):
            logger.debug(f"Current file: {line}")
            if Path(line).is_file() and line not in self.ignored_files:
                logger.debug(f"File to add: {line}")
                self.add_to_index(line.rstrip(os.sep))

    def add_to_index(self, path: str) -> None:
        """Добавление одного файла в индекс
        :param path=Норм. относительный путь до файла"""
        file_content = bytearray()
        with open(path, "br") as file:
            file_content += file.read()
        hash_content = hashlib.sha1(file_content).hexdigest()
        blob_path = os.path.join(self.path_to_objects, hash_content)
        if self.indexed_files.get(path) == hash_content:  # TODO: Чекнуть валидность такого сравнения путей
            logger.debug("skipped file: " + path)
            return

        if path in self.indexed_files:
            self.update_index(path)
        self.indexed_files[path] = hash_content
        with open(blob_path, "bw") as file:
            file.write(zlib.compress(file_content))
        with open(self.path_to_index, "a") as index:
            index.write(f"{path} {hash_content}\n")

    def get_ignored_files(self) -> set:
        """Получение списка всех игнорируемых файлов"""
        if not self.is_init or not os.path.exists(self.path_to_ignore):
            return set()
        result = set()
        with open(self.path_to_ignore, "r") as file:
            for line in file.readlines():
                current_path = os.path.join(line.rstrip("\n"), "**")
                for path in glob.glob(current_path, recursive=True):
                    result.add(path)
        return result

    def update_index(self, path: str):
        """Обновляет запись в индексе, если файл path индексирован"""
        with open(self.path_to_index, "r") as index:
            lines = index.readlines()
        with open(self.path_to_index, "w") as index:
            for line in lines:
                if line.split(" ")[0] != path:  # TODO: Чекнуть валидность такого сравнения путей -> os.path.samefile
                    index.write(line)

    def make_commit(self, message: str):
        root_hash = self.root.get_hash()
        commit_path = os.path.join(self.path_to_objects, root_hash[:2])
        os.mkdir(commit_path)
        with open(os.path.join(commit_path, root_hash[2:]), "w") as commit_obj:
            pass

