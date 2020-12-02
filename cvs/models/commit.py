import hashlib
from pathlib import Path
from cvs.models.tree import TreeNode


class Commit:
    def __init__(self, root: TreeNode, message: str, parent: str):
        self.tree = root
        self.message = message
        self.parent = parent
        self._hash_obj = hashlib.sha1(str(self).encode("utf-8"))

    @property
    def content_hash(self) -> str:
        return self._hash_obj.hexdigest()

    def is_same_with_parent(self, path_to_storage: str) -> bool:
        parent_path = Path(path_to_storage) / self.parent
        if self.parent == "root":
            return False

        commit_content = parent_path.read_text()
        return commit_content.startswith(str(self.tree))

    def create_file(self, destination: str):
        commit_path = Path(destination) / self.content_hash
        commit_path.write_text(str(self))

    def __str__(self):
        return (
            f"{str(self.tree)}\nparent {self.parent}\n\n{self.message}"
        )
