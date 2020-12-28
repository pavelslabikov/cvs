import logging
import fnmatch

from cvs import errors, config
from pathlib import Path
from typing import List, Dict
from cvs.models.blob import Blob
from cvs.utils.factories import BlobFactory

logger = logging.getLogger(__name__)


class FileIndex:
    BLOB_STORAGE = str(config.BLOBS_PATH)

    def __init__(self, path_to_index: Path, path_to_ignore: Path):
        self._location = path_to_index
        if not self._location.exists():
            raise errors.IndexFileNotFoundError(str(path_to_index))
        self.indexed_files = self.get_indexed_files()
        self.ignored_files = self.get_ignored_files(path_to_ignore)

    @property
    def is_empty(self) -> bool:
        return not bool(self.indexed_files)

    @property
    def blobs(self) -> List[Blob]:
        return sorted(self.indexed_files.values())

    def is_ignored(self, filename: str) -> bool:
        for pattern in self.ignored_files:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def add_file(self, path: str) -> None:
        """Добавление файла в индекс"""
        if self.is_ignored(path):
            return

        blob = BlobFactory.create_new_blob(file=path)
        if self.indexed_files.get(path) == blob:
            logger.info(f"File {path} is already indexed!" + blob.content_hash)
            return

        self.indexed_files[path] = blob
        blob.create_file(self.BLOB_STORAGE)

    def get_indexed_files(self) -> Dict[str, Blob]:
        """Извлечение содержимого файла индекса"""
        result = {}
        file_content = self._location.read_text().splitlines()
        for line in file_content:
            filename, hashcode = line.rsplit(" ", 1)
            blob = BlobFactory.get_existing_blob(
                file=filename, hashcode=hashcode
            )
            result[filename] = blob
        return result

    def refresh_file(self) -> None:
        """Запись содержимого индекса в файл"""
        content_to_write = []
        for blob in self.blobs:
            if (
                Path(blob.filename).exists()
                and not self.is_ignored(blob.filename)
            ):
                content_to_write.append(str(blob))
        self._location.write_text("\n".join(content_to_write))

    @staticmethod
    def get_ignored_files(ignore_file: Path) -> List[str]:
        """Получение списка всех игнорируемых файлов"""
        ignore_list = [".cvs/**/*", ".cvs/*"]
        if not ignore_file.exists():
            return ignore_list
        for pattern in ignore_file.read_text().split("\n"):
            if pattern.endswith("/"):
                ignore_list.append(f"{pattern}**/*")
                ignore_list.append(f"{pattern}*")
            else:
                ignore_list.append(pattern)
        return ignore_list
