import anytree

from pathlib import Path
from cvs.models.blob import Blob
from cvs.models.commit import Commit
from cvs.models.tree import TreeNode


class FileCreator:
    @staticmethod
    def create_commit_file(commit: Commit, destination: str):
        commit_path = Path(destination) / commit.get_hash()
        commit_path.write_text(str(commit))

    @staticmethod
    def create_blob_file(blob: Blob, destination: str):
        path_to_blob = Path(destination) / blob.content_hash
        with path_to_blob.open("bw") as file:
            file.write(bytes(blob))

    @staticmethod
    def create_tree_files(start_tree: TreeNode, destination: str):
        for tree in anytree.LevelOrderIter(start_tree, lambda node: not node.is_leaf):
            curr_obj_path = Path(destination) / tree.get_hash()
            content = [str(child) for child in tree.children]
            with curr_obj_path.open("w") as file:
                file.write("\n".join(content))
