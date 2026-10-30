import pytest
from implementation import LibraryManager


@pytest.fixture
def library():
    return LibraryManager()
