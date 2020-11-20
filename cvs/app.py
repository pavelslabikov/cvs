import os
import ctypes
import sys
import hashlib
import zlib
import glob
import logging
from cvs.models import TreeNode, FileIndex
from cvs import const
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class VersionsSystem:
    def __init__(self):
        self.path_to_objects = os.path.join(".cvs", "objects")
        self.path_to_index = os.path.join(".cvs", "index")
        self.path_to_head = os.path.join(".cvs", "HEAD")
        self.path_to_ignore = ".ignore"
        self.path_to_refs = os.path.join(".cvs", "refs")
        self.root = TreeNode(".")

    def init_command(self):
        os.mkdir(".cvs")
        os.mkdir(self.path_to_refs)
        os.mkdir(self.path_to_objects)
        with open(self.path_to_index, "w"):
            pass
        with open(self.path_to_head, "w") as file:
            file.write(os.path.join(".cvs", "refs", "master"))

    def add_command(self, path: str):
        current_index = FileIndex(const.INDEX_PATH)
        path_to_crawl = os.path.join(path, "**")
        for line in glob.glob(path_to_crawl, recursive=True):
            if Path(line).is_file():
                current_index.add_file(os.path.relpath(line))
        current_index.refresh_index_file()

    def make_commit(self, message: str):
        self.build_tree()
        root_hash = self.root.get_hash()
        commit_content = f"tree {root_hash}\n" \
                         f"parent {self.get_last_commit()}\n\n" \
                         f"{message}"
        commit_hash = hashlib.sha1(commit_content.encode("utf-8")).hexdigest()
        commit_path = os.path.join(self.path_to_objects, commit_hash)
        with open(self.path_to_head, "r") as file:
            current_branch = file.read()
        with open(current_branch, "w") as file:
            file.write(commit_hash)
        with open(commit_path, "w") as commit_obj:
            commit_obj.write(commit_content)
        self.create_tree_objects(self.root)

    def get_last_commit(self) -> str:
        with open(self.path_to_head, "r") as file:
            path_to_branch = file.read()
        if not os.path.exists(path_to_branch):
            return "root"
        with open(path_to_branch, "r") as file:
            return file.read()

    def log_command(self):
        with open(self.path_to_head, "r") as file:
            path_to_branch = file.read()
        logger.debug(f"Path to branch in HEAD: {path_to_branch}")
        if not os.path.exists(path_to_branch):
            print(f"No commit history for branch {path_to_branch}")
            return
        with open(path_to_branch, "r") as file:
            last_commit = file.read()
        logger.debug(f"Last commit hash: {last_commit}")
        while last_commit != "root":
            logger.debug(f"Current commit hash: {last_commit}")
            path_to_commit = os.path.join(self.path_to_objects, last_commit)
            with open(path_to_commit, "r") as file:
                commit_content = file.readlines()
                print(commit_content)
                last_commit = commit_content[1].split(" ")[1].rstrip("\n")

    def build_tree(self):
        with open(self.path_to_index, "r") as index:
            for line in index.readlines():
                if not line.rstrip("\n"):
                    continue
                path, blob_name = line.split(" ")
                path_to_blob = os.path.join(".cvs", "objects", blob_name.rstrip("\n"))
                file_content = bytearray()
                with open(path_to_blob, "br") as file:
                    file_content += file.read()
                file_content = zlib.decompress(file_content)
                file_content = file_content + path.encode("utf-8")
                curr_node = self.root
                for file in path.split(os.sep):
                    if curr_node.has_child(file):
                        curr_node.update_hash(file_content)
                        curr_node = curr_node.get_child(file)
                    else:
                        new_node = TreeNode(file)
                        curr_node.add_child(new_node)
                        curr_node.update_hash(file_content)
                        curr_node = new_node
                curr_node.update_hash(file_content)

    def create_tree_objects(self, start_tree: TreeNode):
        if start_tree.get_type() == "blob":
            return
        curr_obj_path = os.path.join(self.path_to_objects, start_tree.get_hash())
        with open(curr_obj_path, "w") as file:
            for filename, tree in start_tree.children.items():
                file.write(f"{tree.get_type()} {tree.get_hash()} {tree.name}\n")
        for tree in start_tree.children.values():
            self.create_tree_objects(tree)
