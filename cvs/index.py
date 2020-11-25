import logging
import os
from pathlib import Path
from typing import Set, List, Dict
from cvs import const
from cvs.blobs import Blob, BlobManager

logger = logging.getLogger(__name__)


class FileIndex:
    def __init__(self, path_to_index: str):
        self.path = path_to_index
        self._indexed_files = self.extract_from_index()
        self._ignored_files = self.get_ignored_files()

    @property
    def is_empty(self) -> bool:
        return not bool(self._indexed_files)

    @property
    def blobs(self) -> List[Blob]:
        return sorted(self._indexed_files.values())

    def add_file(self, path: str) -> None:
        """Добавление файла в индекс"""
        if path in self._ignored_files:
            return

        blob = BlobManager.create_new_blob(file=path)
        self._indexed_files[path] = blob
        blob_path = os.path.join(const.OBJECTS_PATH, blob.content_hash)  # TODO: refactor
        with open(blob_path, "bw") as file:
            file.write(blob.compressed_data)

    def extract_from_index(self) -> Dict[str, Blob]:
        """Извлечение содержимого файла индекса"""
        result = {}
        with open(self.path, "r") as index:
            for line in index.readlines():
                filename, hashcode = line.rstrip("\n").split(" ")
                blob = BlobManager.get_existing_blob(
                    file=filename,
                    hashcode=hashcode
                )
                result[filename] = blob
        return result

    def refresh_index_file(self) -> None:  # TODO: refactor
        """Запись содержимого индекса в файл"""
        with open(self.path, "w") as file:
            for blob in self.blobs:
                if Path(blob.filename).exists() and \
                        blob.filename not in self._ignored_files:
                    file.write(str(blob) + "\n")

    @staticmethod
    def get_ignored_files() -> Set[str]:
        """Получение списка всех игнорируемых файлов"""
        result = set()
        ignore_list = [".cvs"]
        if os.path.exists(".ignore"):
            ignore_list.extend(Path(".ignore").read_text().split("\n"))
        for line in filter(lambda x: x, ignore_list):
            if line.endswith("/"):
                line += "/**/*"
            for path in Path().glob(line):
                result.add(str(path))
        return result
