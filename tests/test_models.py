from pathlib import Path

import pytest
from cvs.models.blob import Blob
from cvs.models.commit import Commit
from cvs.models.index import FileIndex
from cvs.models.tree import TreeNode


@pytest.mark.parametrize(
    "blob",
    [
        Blob("test", b"123"),
    ],
)
def test_creating_blob_file(temp_dir, blob: Blob):
    test_path = Path(temp_dir.name)
    blob.create_file(test_path)
    expected_file = test_path / blob.content_hash
    assert expected_file.exists()


@pytest.mark.parametrize(
    "commit",
    [
        Commit(TreeNode("test"), "msg", "root")
    ],
)
def test_creating_commit_file(temp_dir, commit: Commit):
    test_path = Path(temp_dir.name)
    commit.create_file(test_path)
    assert (test_path / commit.content_hash).exists()


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
