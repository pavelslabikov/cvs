from cvs.app import VersionsSystem
from cvs.view import TestView

import pytest
import tempfile


@pytest.fixture()
def testing_app():
    return VersionsSystem(TestView())


@pytest.fixture()
def temp_dir():
    return tempfile.TemporaryDirectory(dir="tests/")
