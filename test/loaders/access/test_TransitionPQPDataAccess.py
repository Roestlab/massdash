"""
test/loaders/access/test_TransitionPQPDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import pytest

from massdash.loaders.access.TransitionPQPDataAccess import TransitionPQPDataAccess
from massdash.testing import PandasSnapshotExtension
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def data_access():
    filename = f"{TEST_PATH}/test_data/example_dia/openswath/lib/test.pqp"
    data_access = TransitionPQPDataAccess(filename)
    yield data_access
    data_access.close()

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

def test_getTransitionList(data_access, snapshot_pandas):
    # test getTransitionList() method
    transitions = data_access.getTransitionList()
    assert snapshot_pandas == transitions 

def test_validate_columns(data_access):
    # test _validate_columns() method
    data_access.data = data_access.getTransitionList()
    assert data_access._validate_columns()

def test_load(data_access, snapshot_pandas):
    # test load() method
    data_access.load()
    assert snapshot_pandas == data_access.data 

def test_empty(data_access):
    # test empty() method
    data_access.load()
    assert not data_access.empty()