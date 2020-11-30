import hashlib
import os
import zlib
import anytree

from cvs import config
from pathlib import Path
from typing import Iterable
from cvs.models.blob import Blob
from cvs.models.commit import Commit
from cvs.models.tree import TreeNode


class TreeFactory:
    @classmethod
    def create_new_tree(cls, blobs: Iterable[Blob]) -> TreeNode:
        root = TreeNode(".")
        for blob in blobs:
            file_content = bytes.fromhex(blob.content_hash)
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


class BlobFactory:
    @classmethod
    def get_existing_blob(cls, file: str, hashcode: str) -> Blob:
        path_to_blob = config.BLOBS_PATH / hashcode
        compressed_data = path_to_blob.read_bytes()
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def create_new_blob(cls, file: str) -> Blob:
        compressed_data = cls._get_compressed_content(file)
        hashcode = hashlib.sha1(compressed_data).hexdigest()
        return Blob(file, hashcode, compressed_data)

    @classmethod
    def _get_compressed_content(cls, file: str) -> bytes:
        file_content = Path(file).read_bytes()
        return zlib.compress(file_content)


class CommitFactory:
    @classmethod
    def create_new_commit(cls, tree: TreeNode, message: str) -> Commit:
        current_branch = config.HEAD_PATH.read_text()
        if not os.path.exists(current_branch):
            return Commit(tree, message, "root")
        with open(current_branch, "r") as file:
            return Commit(tree, message, file.read())
