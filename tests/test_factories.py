import pytest
import hashlib
import zlib

from cvs.utils import factories
from cvs.models.blob import Blob
from pathlib import Path


@pytest.mark.parametrize(
    "filename, data", [("test_file", b""), ("123", b"123")]
)
def test_creating_blob(temp_dir, filename: str, data: bytes):
    test_file = Path(temp_dir.name) / filename
    test_file.write_bytes(data)
    compressed_data = zlib.compress(data)
    expected_blob = Blob(str(test_file), compressed_data)
    actual_blob = factories.BlobFactory.create_new_blob(str(test_file))
    assert actual_blob == expected_blob


@pytest.mark.parametrize(
    "blobs",
    [
        [Blob("1", b"456"), Blob("", b"")],
    ],
)
def test_creating_tree(blobs: list):
    actual_tree = factories.TreeFactory.create_new_tree(blobs)
    hashcode = hashlib.sha1()
    for blob in blobs:
        hashcode.update(blob.compressed_data)
    assert hashcode.hexdigest() == actual_tree.content_hash
    assert actual_tree.parent is None
