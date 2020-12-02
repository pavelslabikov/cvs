import logging

from cvs import errors, config
from pathlib import Path
from typing import Set, List, Dict
from cvs.models.blob import Blob
from cvs.utils.factories import BlobFactory

logger = logging.getLogger(__name__)


class FileIndex:
    BLOB_STORAGE = str(config.BLOBS_PATH)

    def __init__(self, path_to_index: str, path_to_ignore: str):
        self._location = Path(path_to_index)
        if not self._location.exists():
            raise errors.IndexFileNotFoundError(path_to_index)
        self.indexed_files = self.get_indexed_files()
        self._ignored_files = self.get_ignored_files(path_to_ignore)

    @property
    def is_empty(self) -> bool:
        return not bool(self.indexed_files)

    @property
    def blobs(self) -> List[Blob]:
        return sorted(self.indexed_files.values())

    def add_file(self, path: str) -> None:
        """Добавление файла в индекс"""
        if path in self._ignored_files:
            return

        blob = BlobFactory.create_new_blob(file=path)
        if self.indexed_files.get(path) == blob:
            logger.info(f"File {path} is already indexed!")
            return

        self.indexed_files[path] = blob
        blob.create_file(self.BLOB_STORAGE)

    def get_indexed_files(self) -> Dict[str, Blob]:
        """Извлечение содержимого файла индекса"""
        result = {}
        file_content = self._location.read_text().splitlines()
        for line in file_content:
            filename, hashcode = line.split(" ")
            blob = BlobFactory.get_existing_blob(
                file=filename,
                hashcode=hashcode
            )
            result[filename] = blob
        return result

    def refresh_file(self) -> None:
        """Запись содержимого индекса в файл"""
        content_to_write = []
        for blob in self.blobs:
            if Path(blob.filename).exists() and \
                    blob.filename not in self._ignored_files:
                content_to_write.append(str(blob))
        self._location.write_text("\n".join(content_to_write))

    @staticmethod
    def get_ignored_files(ignore_file: str) -> Set[str]:
        """Получение списка всех игнорируемых файлов"""
        result = set()
        ignore_list = [".cvs/"]
        ignore_file = Path(ignore_file)
        if ignore_file.exists():
            ignore_list.extend(ignore_file.read_text().split("\n"))
        for line in filter(lambda x: x, ignore_list):
            if line.endswith("/"):
                line += "/**/*"
            for path in Path().glob(line):
                result.add(str(path))
        return result
