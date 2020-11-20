from typing import Dict
import hashlib
import os
import zlib
import logging
import glob
from cvs import const

logger = logging.getLogger(__name__)


class TreeNode:
    def __init__(self, name: str):
        self.name = name
        self.hash = hashlib.sha1()
        self.children: Dict[str, TreeNode] = dict()

    def get_hash(self) -> str:
        return self.hash.hexdigest()

    def has_child(self, name: str) -> bool:
        return name in self.children

    def get_child(self, name: str) -> 'TreeNode':
        return self.children[name]

    def update_hash(self, hash_code: bytes) -> None:
        self.hash.update(hash_code)

    def add_child(self, node: 'TreeNode'):
        self.children[node.name] = node

    def get_type(self) -> str:
        if bool(self.children):
            return "tree"
        return "blob"


class FileIndex:
    def __init__(self, path_to_index: str):
        self.path = path_to_index
        self.content = self.extract_from_index()
        self.ignored_files = self.get_ignored_files()

    @property
    def is_empty(self) -> bool:
        return not bool(self.content)

    def add_file(self, path: str) -> None:
        """Добавление файла в индекс"""
        if path in self.ignored_files:
            logger.info(f"File {path} is ignored")
            return
        file_content = bytearray()
        with open(path, "br") as file:
            file_content += file.read()
        content_to_hash = file_content + path.encode("utf-8")
        hash_content = hashlib.sha1(content_to_hash).hexdigest()
        blob_path = os.path.join(const.OBJECTS_PATH, hash_content)
        if self.content.get(path) == hash_content:
            logger.info(f"File {path} is already indexed")
            return

        self.content[path] = hash_content
        with open(blob_path, "bw") as file:
            file.write(zlib.compress(file_content))

    def extract_from_index(self) -> Dict[str, str]:
        """Извлечение содержимого файла индекса"""
        result = {}
        with open(self.path, "r") as index:
            for line in index.readlines():
                path, content_hash = line.rstrip("\n").split(" ")
                result[path] = content_hash
        return result

    def refresh_index_file(self) -> None:
        """Запись содержимого индекса в файл"""
        with open(self.path, "w") as file:
            for path, hash_content in self.content.items():
                if os.path.exists(path) and path not in self.ignored_files:
                    logger.info(f"Adding file {path} to index file")
                    file.write(f"{path} {hash_content}\n")

    @staticmethod
    def get_ignored_files() -> set:
        """Получение списка всех игнорируемых файлов"""
        result = set(".cvs")
        if not os.path.exists(const.IGNORE_PATH):
            return result

        with open(const.IGNORE_PATH, "r") as file:
            for line in file.readlines():
                current_path = os.path.join(line.rstrip("\n"), "**")
                for path in glob.glob(current_path, recursive=True):
                    result.add(os.path.relpath(path))
        return result
