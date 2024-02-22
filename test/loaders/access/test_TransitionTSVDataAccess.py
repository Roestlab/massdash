from pathlib import Path
import pytest
import pandas as pd

from massdash.loaders.access.TransitionTSVDataAccess import TransitionTSVDataAccess
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture
def data_access():
    return TransitionTSVDataAccess(f"{TEST_PATH}/test_data/example_dia/diann/lib/test_1_lib.tsv")

def test_resolve_column_names(data_access, snapshot_pandas):
    data_access.data = pd.read_csv(data_access.filename, sep='\t')
    data_access._resolve_column_names()
    assert snapshot_pandas == data_access.data

def test_generate_annotation(data_access, snapshot_pandas):
    data_access.data = pd.read_csv(data_access.filename, sep='\t')
    data_access._resolve_column_names()
    data_access.generate_annotation()
    assert snapshot_pandas == data_access.data

def test_validate_columns(data_access):
    data_access.data = pd.read_csv(data_access.filename, sep='\t')
    data_access._resolve_column_names()
    data_access.generate_annotation()
    data_access._validate_columns()
    assert data_access._validate_columns()

def test_load(data_access, snapshot_pandas):
    data_access.load()
    assert snapshot_pandas == data_access.data

def test_empty(data_access):
    data_access.load()
    assert not data_access.empty()