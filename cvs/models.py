from typing import Dict, List
from cvs.blobs import Blob
from pathlib import Path
import hashlib
import logging
import os

logger = logging.getLogger(__name__)


class TreeNode:
    def __init__(self, name: str):
        self.name = name
        self.hash = hashlib.sha1()
        self.children: Dict[str, TreeNode] = dict()

    def get_hash(self) -> str:
        return self.hash.hexdigest()

    def has_child(self, name: str) -> bool:
        return name in self.children

    def get_child(self, name: str) -> 'TreeNode':
        return self.children[name]

    def update_hash(self, hash_code: bytes) -> None:
        self.hash.update(hash_code)

    def add_child(self, node: 'TreeNode'):
        self.children[node.name] = node

    def get_type(self) -> str:
        if bool(self.children):
            return "tree"
        return "blob"


class TreeManager:
    TREE_STORAGE = Path(".cvs", "objects")

    @classmethod
    def create_new_tree(cls, blobs: List[Blob]) -> TreeNode:
        root = TreeNode(".")
        for blob in blobs:
            file_content = blob.compressed_data
            curr_node = root
            for file in blob.filename.split(os.sep):
                curr_node.update_hash(file_content)
                if curr_node.has_child(file):
                    curr_node = curr_node.get_child(file)
                else:
                    new_node = TreeNode(file)
                    curr_node.add_child(new_node)
                    curr_node = new_node
            curr_node.update_hash(file_content)
        return root

    @classmethod
    def get_existing_tree(cls, tree_name: str, tree_hash: str):
        pass

    @classmethod
    def create_tree_objects(cls, start_tree: TreeNode):
        if start_tree.get_type() == "blob":
            return
        curr_obj_path = cls.TREE_STORAGE / start_tree.get_hash()
        with curr_obj_path.open("w") as file:
            for filename, tree in start_tree.children.items():
                file.write(f"{tree.get_type()} {tree.get_hash()} {tree.name}\n")
        for tree in start_tree.children.values():
            cls.create_tree_objects(tree)


class Commit:
    def __init__(self, root_hash: str, message: str, parent: str):
        self.root_hash = root_hash
        self.message = message
        self.parent = parent

    def __str__(self):
        return f"tree {self.root_hash}\n" \
               f"parent {self.parent}\n\n" \
               f"{self.message}"
