import hashlib
from pathlib import Path
from cvs.models.tree import TreeNode


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
