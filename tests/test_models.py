from pathlib import Path

import pytest
from cvs.models.blob import Blob
from cvs.models.index import FileIndex


@pytest.mark.parametrize(
    "blob",
    [
        Blob("test", b"123"),
    ],
)
def test_creating_blob_file(temp_dir, blob: Blob):
    blob.create_file(temp_dir.name)
    expected_file = Path(temp_dir.name) / blob.content_hash
    assert expected_file.exists()


@pytest.mark.parametrize("path, file_content", [("test", "")])
def test_adding_to_index(temp_dir, path: str, file_content: str):
    file_to_add = Path(temp_dir.name) / path
    file_to_add.write_text(file_content)
    test_index = Path(temp_dir.name) / "index"
    test_index.write_text("")
    index = FileIndex(test_index, Path("tests/.ignore"))
    index.BLOB_STORAGE = temp_dir.name
    index.add_file(str(file_to_add))
    assert str(file_to_add) in index.indexed_files
