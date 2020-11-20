from typing import Dict
import hashlib


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
