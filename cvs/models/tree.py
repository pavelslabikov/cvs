import hashlib
from pathlib import Path
from anytree import NodeMixin, LevelOrderIter


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

    def create_file(self, destination: str) -> None:
        for tree in LevelOrderIter(self, lambda node: not node.is_leaf):
            curr_obj_path = Path(destination) / tree.get_hash()
            content = [str(child) for child in tree.children]
            with curr_obj_path.open("w") as file:
                file.write("\n".join(content))

    def __str__(self):
        obj_type = "blob" if self.is_leaf else "tree"
        return f"{obj_type} {self.get_hash()} {self.name}"
