"""
test/loaders/test_ResultsLoader.py
"""

from pathlib import Path
import pytest
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import ResultsLoader
from massdash.util import find_git_directory
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture(params=[
    f"{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw",
    f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv",
    #[f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv", f"{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw"],
    #f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv",
    #[f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv", f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv"]
])
def resultsLoader(request):
    return ResultsLoader(rsltsFile=request.param, libraryFile=None, verbose=False, mode='module')

@pytest.fixture(params=['AGAANIVPNSTGAAK', 'INVALID'])
def precursor(request):
    return request.param

@pytest.fixture(params=[2])
def charge(request):
    return request.param

def test_loadTransitionGroupFeatures(resultsLoader, precursor, charge, snapshot):
    features = resultsLoader.loadTransitionGroupFeatures(precursor, charge)
    assert snapshot == AmberDataSerializer.serialize(features)

def test_loadTopTransitionGroupFeature(resultsLoader, precursor, charge, snapshot):
    top_feature = resultsLoader.loadTopTransitionGroupFeature(precursor, charge)
    assert snapshot == AmberDataSerializer.serialize(top_feature)

def test_loadTopTransitionGroupFeatureDf(resultsLoader, precursor, charge, snapshot_pandas):
    top_feature = resultsLoader.loadTopTransitionGroupFeatureDf(precursor, charge)
    top_feature = top_feature.sort_values(by=['consensusApex'], ascending=True)
    assert snapshot_pandas == top_feature

def test_loadTopTransitionGroupFeaturesDf(resultsLoader, precursor, charge, snapshot_pandas):
    feature = resultsLoader.loadTransitionGroupFeaturesDf(precursor, charge)
    feature = feature.sort_values(by=['consensusApex'], ascending=True)
    assert snapshot_pandas == feature