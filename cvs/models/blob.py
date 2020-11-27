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
