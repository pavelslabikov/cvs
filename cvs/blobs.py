import hashlib
import zlib
from pathlib import Path


class Blob:
    def __init__(self, filename: str, hashcode: str, data: bytes):
        self._filename = filename
        self._content_hash = hashcode
        self.compressed_data = data

    @property
    def content_hash(self) -> str:
        return self._content_hash

    @property
    def filename(self) -> str:
        return self._filename

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return f"{self._filename} {self._content_hash}"


class BlobManager:
    BLOB_STORAGE = Path(".cvs/objects")

    @classmethod
    def get_existing_blob(cls, file: str, hashcode: str) -> Blob:
        path_to_blob = cls.BLOB_STORAGE / hashcode
        compressed_data = path_to_blob.read_bytes()
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def create_new_blob(cls, file: str) -> Blob:
        compressed_data = cls._get_compressed_content(file)
        hashcode = cls._evaluate_hash(compressed_data)
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def _evaluate_hash(cls, data: bytes) -> str:
        return hashlib.sha1(data).hexdigest()

    @classmethod
    def _get_compressed_content(cls, file: str) -> bytes:
        file_content = Path(file).read_bytes()
        return zlib.compress(file_content)
