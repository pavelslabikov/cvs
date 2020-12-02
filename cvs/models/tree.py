import hashlib
from pathlib import Path
from anytree import NodeMixin, LevelOrderIter


class TreeNode(NodeMixin):
    def __init__(self, name: str, parent=None):
        super(TreeNode, self).__init__()
        self.name = name
        self._hash_obj = hashlib.sha1()
        self.parent = parent

    @property
    def content_hash(self) -> str:
        return self._hash_obj.hexdigest()

    def update_hash(self, hash_code: bytes) -> None:
        self._hash_obj.update(hash_code)

    def create_file(self, destination: str) -> None:
        for tree in LevelOrderIter(self, lambda node: not node.is_leaf):
            curr_obj_path = Path(destination) / tree.content_hash
            content = [str(child) for child in tree.children]
            with curr_obj_path.open("w") as file:
                file.write("\n".join(content))

    def __str__(self):
        obj_type = "blob" if self.is_leaf else "tree"
        return f"{obj_type} {self.content_hash} {self.name}"
