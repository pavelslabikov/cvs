import hashlib
from anytree import NodeMixin


class TreeNode(NodeMixin):
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
