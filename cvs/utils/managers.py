import hashlib
import os
import zlib
import anytree

from pathlib import Path
from typing import Iterable
from cvs.models.blob import Blob
from cvs.models.commit import Commit
from cvs.models.tree import TreeNode

OBJECT_STORAGE = Path(".cvs", "objects")


class TreeManager:
    @classmethod
    def create_new_tree(cls, blobs: Iterable[Blob]) -> TreeNode:
        root = TreeNode(".")
        for blob in blobs:
            file_content = blob.compressed_data
            curr_node = root
            for file in blob.filename.split(os.sep):
                curr_node.update_hash(file_content)
                child = anytree.search.find(curr_node, lambda node: node.name == file)
                if child:
                    curr_node = child
                else:
                    curr_node = TreeNode(file, parent=curr_node)
            curr_node.update_hash(file_content)
        return root

    @classmethod
    def create_tree_files(cls, start_tree: TreeNode) -> None:
        for tree in anytree.LevelOrderIter(start_tree, lambda node: not node.is_leaf):
            curr_obj_path = OBJECT_STORAGE / tree.get_hash()
            content = []
            for child in tree.children:
                content.append(str(child))
            with curr_obj_path.open("w") as file:
                file.write("\n".join(content))


class BlobManager:
    @classmethod
    def get_existing_blob(cls, file: str, hashcode: str) -> Blob:
        path_to_blob = OBJECT_STORAGE / hashcode
        compressed_data = path_to_blob.read_bytes()
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def create_new_blob(cls, file: str) -> Blob:
        compressed_data = cls._get_compressed_content(file)
        hashcode = cls._evaluate_hash(compressed_data)
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def create_blob_file(cls, blob: Blob) -> None:
        """Создание файла по объекту Blob"""
        path_to_blob = OBJECT_STORAGE / blob.content_hash
        with path_to_blob.open("bw") as file:
            file.write(blob.compressed_data)

    @classmethod
    def _evaluate_hash(cls, data: bytes) -> str:
        return hashlib.sha1(data).hexdigest()

    @classmethod
    def _get_compressed_content(cls, file: str) -> bytes:
        file_content = Path(file).read_bytes()
        return zlib.compress(file_content)


class CommitManager:
    @classmethod
    def create_new_commit(cls, tree: TreeNode, message: str) -> Commit:
        current_branch = Path(".cvs/HEAD").read_text()
        if not os.path.exists(current_branch):
            return Commit(tree, message, "root")
        with open(current_branch, "r") as file:
            return Commit(tree, message, file.read())

    @classmethod
    def create_commit_file(cls, commit: Commit):
        commit_path = OBJECT_STORAGE / commit.get_hash()
        commit_path.write_text(str(commit))
