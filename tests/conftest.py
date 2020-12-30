import shutil
from pathlib import Path

import pytest
import tempfile

from cvs.view import TestView


@pytest.fixture()
def temp_dir():
    return tempfile.TemporaryDirectory(dir="tests/")


@pytest.fixture()
def test_view():
    return TestView()


@pytest.fixture()
def test_dir():
    if Path(".cvs").exists():
        shutil.rmtree(".cvs")
    yield
    shutil.rmtree(".cvs")
