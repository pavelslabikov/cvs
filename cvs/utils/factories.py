import os
import zlib

from cvs import config
from pathlib import Path
from anytree import search
from typing import Iterable
from cvs.models.blob import Blob
from cvs.models.commit import Commit
from cvs.models.tree import TreeNode


class TreeFactory:
    @classmethod
    def create_new_tree(cls, blobs: Iterable[Blob]) -> TreeNode:
        root = TreeNode(".")
        for blob in blobs:
            file_content = blob.compressed_data
            curr_node = root
            for file in blob.filename.split(os.sep):
                curr_node.update_hash(file_content)
                child = search.find(curr_node, lambda node: node.name == file)
                if child:
                    curr_node = child
                else:
                    curr_node = TreeNode(file, parent=curr_node)
            curr_node.update_hash(file_content)
        return root


class BlobFactory:
    @classmethod
    def get_existing_blob(cls, file: str, hashcode: str) -> Blob:
        path_to_blob = config.BLOBS_PATH / hashcode
        compressed_data = path_to_blob.read_bytes()
        return Blob(file, compressed_data)

    @classmethod
    def create_new_blob(cls, file: str) -> Blob:
        file_content = Path(file).read_bytes()
        compressed_data = zlib.compress(file_content)
        return Blob(file, compressed_data)


class CommitFactory:
    @classmethod
    def create_new_commit(cls, tree: TreeNode, message: str) -> Commit:
        current_branch = config.HEAD_PATH.read_text()
        parent_path = config.REFS_PATH / current_branch
        if not parent_path.exists():
            parent = Commit.parse_file_content(current_branch)[1]
            return Commit(tree, message, parent)
        return Commit(tree, message, parent_path.read_text())
