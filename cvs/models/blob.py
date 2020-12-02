import hashlib
from pathlib import Path


class Blob:
    def __init__(self, filename: str, data: bytes):
        self._filename = filename
        self._compressed_data = data
        self._hash_obj = hashlib.sha1(data)

    @property
    def content_hash(self) -> str:
        return self._hash_obj.hexdigest()

    @property
    def filename(self) -> str:
        return self._filename

    def create_file(self, destination: str) -> None:
        path_to_blob = Path(destination) / self.content_hash
        path_to_blob.write_bytes(self._compressed_data)

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, Blob):
            return False
        return (
            self.filename == other.filename
            and self.content_hash == other.content_hash
        )

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return f"{self._filename} {self.content_hash}"
