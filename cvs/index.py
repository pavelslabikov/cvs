import hashlib
import os
import zlib
from pathlib import Path
from typing import Dict, Set
from cvs import const
from cvs.models import logger


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
        current_file = Path(path)
        if current_file in self.ignored_files:
            logger.info(f"File {current_file} is ignored")
            return

        file_content = current_file.read_bytes()
        content_to_hash = file_content + str(current_file).encode("utf-8")
        hash_content = hashlib.sha1(content_to_hash).hexdigest()
        blob_path = os.path.join(const.OBJECTS_PATH, hash_content)
        if self.content.get(current_file) == hash_content:
            logger.info(f"File {current_file} is already indexed")
            return

        self.content[current_file] = hash_content
        with open(blob_path, "bw") as file:
            file.write(zlib.compress(file_content))

    def extract_from_index(self) -> Dict[Path, str]:
        """Извлечение содержимого файла индекса"""
        result = {}
        with open(self.path, "r") as index:
            for line in index.readlines():
                filename, content_hash = line.rstrip("\n").split(" ")
                result[Path(filename)] = content_hash
        return result

    def refresh_index_file(self) -> None:
        """Запись содержимого индекса в файл"""
        with open(self.path, "w") as file:
            for path, hash_content in self.content.items():
                if path.exists() and path not in self.ignored_files:
                    logger.info(f"Writing {path} to index file")
                    file.write(f"{path} {hash_content}\n")

    @staticmethod
    def get_ignored_files() -> Set[Path]:
        """Получение списка всех игнорируемых файлов"""
        result = set()
        ignore_list = [".cvs"]
        if os.path.exists(".ignore"):
            ignore_list.extend(Path(".ignore").read_text().split("\n"))
        for line in ignore_list:
            if line.startswith("#") or not line:
                continue
            if line.endswith("/"):
                for path in Path().glob(line + "/**/*"):
                    result.add(path)
            else:
                for path in Path().glob(line):
                    result.add(path)
        return result
