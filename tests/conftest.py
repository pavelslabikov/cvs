import pytest
import tempfile


@pytest.fixture()
def temp_dir():
    return tempfile.TemporaryDirectory(dir="tests/")
