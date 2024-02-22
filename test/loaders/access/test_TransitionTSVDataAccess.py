import pytest
from massdash.loaders.access.TransitionTSVDataAccess import TransitionTSVDataAccess
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
import pandas as pd

@pytest.fixture
def filename():
    return "../../test_data/example_dia/diann/lib/test_1_lib.tsv"

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture
def data_access():
    return TransitionTSVDataAccess("../../test_data/example_dia/diann/lib/test_1_lib.tsv")

def test_resolve_column_names(data_access, snapshot_pandas):
    data_access.data = pd.read_csv(data_access.filename, sep='\t')
    data_access._resolve_column_names()
    assert snapshot_pandas == data_access.data

def test_generate_annotation(data_access, snapshot):
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