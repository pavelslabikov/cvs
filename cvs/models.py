from typing import Set, List


class TreeNode:
    def __init__(self, name: str):
        self.name = name
        self.children: Set[TreeNode] = set()
        self.files: List[str] = []

    def get_hash(self) -> str:
        pass