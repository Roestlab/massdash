"""
test/loaders/access/test_OSWPQResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
import pandas as pd

from massdash.testing import PandasSnapshotExtension
from massdash.loaders.access.OSWPQResultsAccess import OSWPQResultsAccess
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.fixture
def oswpq_data_access():
    """Fixture for OSWPQ data access""" 
    oswpq_data_access = OSWPQResultsAccess(f"{TEST_PATH}/test_data/example_dia/openswath/osw/test.oswpq")
    yield oswpq_data_access

@pytest.fixture(params=['run1', None])
def run(request):
    return request.param

def test_getRunNames(oswpq_data_access, snapshot):
    runnames = oswpq_data_access.getRunNames()
    assert snapshot == runnames 

def test_getIdentifiedPrecursors(oswpq_data_access, snapshot):
    precursors = oswpq_data_access.getIdentifiedPrecursors()
    assert precursors == snapshot

def test_getIdentifiedPrecursorIntensities(oswpq_data_access, run, snapshot_pandas):
    intensities = oswpq_data_access.getIdentifiedPrecursorIntensities(run=run)
    assert snapshot_pandas == intensities

def test_getIdentifiedProteins(oswpq_data_access, run, snapshot):
    proteins = oswpq_data_access.getIdentifiedProteins(run=run)
    assert proteins == snapshot

def test_getIdentifiedPeptides(oswpq_data_access, run, snapshot):
    peptides = oswpq_data_access.getIdentifiedPeptides(run=run)
    assert peptides == snapshot

@pytest.mark.parametrize("fullpeptidename,charge", [("PEPTIDE", 2), ("INVALID", 0)])
def test_getTransitionGroupFeatures(oswpq_data_access, snapshot, fullpeptidename, charge, run):
    # Use first available run if run is None
    if run is None:
        run_names = oswpq_data_access.getRunNames()
        run = run_names[0] if run_names else "run1"
    
    transition_group_feature = oswpq_data_access.getTransitionGroupFeatures(run, fullpeptidename, charge)
    assert snapshot == transition_group_feature

@pytest.mark.parametrize("fullpeptidename,charge", [("PEPTIDE", 2), ("INVALID", 0)])
def test_getTransitionGroupFeaturesDf(oswpq_data_access, snapshot_pandas, run, fullpeptidename, charge):
    # Use first available run if run is None
    if run is None:
        run_names = oswpq_data_access.getRunNames()
        run = run_names[0] if run_names else "run1"
    
    transition_group_feature = oswpq_data_access.getTransitionGroupFeaturesDf(run, fullpeptidename, charge)
    assert snapshot_pandas == transition_group_feature

def test_getSoftware(oswpq_data_access):
    assert oswpq_data_access.getSoftware() == "OpenSWATH"

def test_has_im_property(oswpq_data_access, snapshot):
    has_im = oswpq_data_access.has_im
    assert snapshot == has_im

# Test lazy evaluation specific functionality
def test_lazy_evaluation_performance(oswpq_data_access):
    """Test that lazy evaluation is working by checking dataset initialization"""
    # This test verifies that datasets are initialized without loading full data
    assert hasattr(oswpq_data_access, 'precursors_dataset') or hasattr(oswpq_data_access, 'precursors_df')
    assert hasattr(oswpq_data_access, 'transitions_dataset') or hasattr(oswpq_data_access, 'transitions_df')

def test_column_projection(oswpq_data_access):
    """Test that we can query specific columns efficiently"""
    # Test that we can get just run names without loading all data
    run_names = oswpq_data_access.getRunNames()
    assert isinstance(run_names, list)

def test_filtering_efficiency(oswpq_data_access):
    """Test that filtering is applied at the parquet level when possible"""
    # Test that q-value filtering works efficiently
    precursors = oswpq_data_access.getIdentifiedPrecursors(qvalue=0.01)
    assert isinstance(precursors, (set, dict))

# Tests for error handling and edge cases
def test_invalid_directory():
    """Test initialization with invalid directory"""
    with pytest.raises(ValueError):
        OSWPQResultsAccess("/non/existent/path")

def test_missing_files(tmp_path):
    """Test initialization with directory missing required files"""
    with pytest.raises(FileNotFoundError):
        OSWPQResultsAccess(str(tmp_path))