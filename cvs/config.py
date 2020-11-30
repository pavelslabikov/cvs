import subprocess
import sys
from pathlib import Path

MAIN_PATH = Path(".cvs")

OBJECTS_PATH = MAIN_PATH / "objects"
COMMITS_PATH = OBJECTS_PATH / "commits"
BLOBS_PATH = OBJECTS_PATH / "blobs"
TREES_PATH = OBJECTS_PATH / "trees"

INDEX_PATH = MAIN_PATH / "index"
REFS_PATH = MAIN_PATH / "refs"
HEAD_PATH = MAIN_PATH / "HEAD"
IGNORE_PATH = Path(".ignore")


def create_dirs():
    MAIN_PATH.mkdir()
    if sys.platform.startswith("win32"):
        subprocess.call(['attrib', '+h', str(MAIN_PATH)])
    OBJECTS_PATH.mkdir()
    COMMITS_PATH.mkdir()
    BLOBS_PATH.mkdir()
    TREES_PATH.mkdir()
    REFS_PATH.mkdir()
