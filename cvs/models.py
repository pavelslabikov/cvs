import hashlib
import logging
import os
import anytree

from typing import Iterable
from cvs.blobs import Blob
from pathlib import Path
from anytree import search


logger = logging.getLogger(__name__)


class TreeNode(anytree.NodeMixin):
    def __init__(self, name: str, parent=None):
        super(TreeNode, self).__init__()
        self.name = name
        self.hash = hashlib.sha1()
        self.parent = parent

    def get_hash(self) -> str:
        return self.hash.hexdigest()

    def update_hash(self, hash_code: bytes) -> None:
        self.hash.update(hash_code)

    def get_type(self) -> str:
        if self.is_leaf:
            return "blob"
        return "tree"

    def __str__(self):
        return f"{self.get_type()} {self.get_hash()} {self.name}"


class TreeManager:
    TREE_STORAGE = Path(".cvs", "objects")

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

    @classmethod
    def create_tree_files(cls, start_tree: TreeNode):
        for tree in anytree.LevelOrderIter(start_tree, lambda node: not node.is_leaf):
            curr_obj_path = cls.TREE_STORAGE / tree.get_hash()
            content = []
            for child in tree.children:
                content.append(str(child))
            with curr_obj_path.open("w") as file:
                file.write("\n".join(content))


class Commit:
    def __init__(self, root: TreeNode, message: str, parent: str):
        self.tree = root
        self.message = message
        self.parent = parent

    def get_hash(self) -> str:
        return hashlib.sha1(str(self).encode("utf-8")).hexdigest()

    def is_same_with_parent(self) -> bool:
        if self.parent == "root":
            return False

        commit_content = Path(f".cvs/objects/{self.parent}").read_text()
        return commit_content.startswith(str(self.tree))

    def __str__(self):
        return f"{str(self.tree)}\n" \
               f"parent {self.parent}\n\n" \
               f"{self.message}"


class CommitManager:
    COMMIT_STORAGE = Path(".cvs", "objects")

    @classmethod
    def create_new_commit(cls, tree: TreeNode, message: str) -> Commit:
        current_branch = Path(".cvs/HEAD").read_text()
        if not os.path.exists(current_branch):
            return Commit(tree, message, "root")
        with open(current_branch, "r") as file:
            return Commit(tree, message, file.read())

