import logging

from cvs import errors, config
from pathlib import Path
from typing import Set, List, Dict
from cvs.models.blob import Blob
from cvs.utils.factories import BlobFactory

logger = logging.getLogger(__name__)


class FileIndex:
    def __init__(self):
        self._location = config.INDEX_PATH
        if not self._location.exists():
            raise errors.IndexFileNotFoundError(str(self._location))
        self._indexed_files = self.get_indexed_files()
        self._ignored_files = self.get_ignored_files(config.IGNORE_PATH)

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

        blob = BlobFactory.create_new_blob(file=path)
        if self._indexed_files.get(path) == blob:
            logger.info(f"File {path} is already indexed!")
            return

        self._indexed_files[path] = blob
        blob.create_file(str(config.BLOBS_PATH))

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

    def refresh_index_file(self) -> None:
        """Запись содержимого индекса в файл"""
        content_to_write = []
        for blob in self.blobs:
            if Path(blob.filename).exists() and \
                    blob.filename not in self._ignored_files:
                content_to_write.append(str(blob))
        self._location.write_text("\n".join(content_to_write))

    @staticmethod
    def get_ignored_files(ignore_file: Path) -> Set[str]:
        """Получение списка всех игнорируемых файлов"""
        result = set()
        ignore_list = [".cvs/"]
        if ignore_file.exists():
            ignore_list.extend(ignore_file.read_text().splitlines())
        for line in ignore_list:
            if line.endswith("/"):
                line += "/**/*"
            for path in Path().glob(line):
                result.add(str(path))
        return result
