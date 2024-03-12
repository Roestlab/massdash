"""
test/loaders/test_ResultsLoader.py
"""

from pathlib import Path
import pytest
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import ResultsLoader
from massdash.util import find_git_directory
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
#from massdash.testing.BokehSnapshotExtension import BokehSnapshotExtension
#from massdash.testing.

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture(params=[
    f"{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw",
    f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv",
    [f"{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv", f"{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw"],
    #f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv",
    #[f"{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv", f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv"]
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
    top_feature = top_feature.sort_values(by=['consensusApex'], ascending=True).reset_index(drop=True)
    assert snapshot_pandas == top_feature

def test_loadTransitionGroupFeaturesDf(resultsLoader, precursor, charge, snapshot_pandas):
    feature = resultsLoader.loadTransitionGroupFeaturesDf(precursor, charge)
    feature = feature.sort_values(by=['consensusApex'], ascending=True).reset_index(drop=True)
    assert snapshot_pandas == feature

def test_loadSoftware(resultsLoader, snapshot):
    assert snapshot == resultsLoader._loadSoftware()

def test_inferRunNames(resultsLoader, snapshot):
    assert snapshot == resultsLoader._inferRunNames()

def test_loadIdentifiedPrecursors(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadIdentifiedPrecursors()

def test_loadNumIdentifiedPrecursors(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadNumIdentifiedPrecursors()

def test_loadIdentifiedProteins(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadIdentifiedProteins()

def test_loadNumIdentifiedProteins(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadNumIdentifiedProteins()

def test_loadIdentifiedPeptides(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadIdentifiedPeptides()

def test_loadNumIdentifiedPeptides(resultsLoader, snapshot):
    assert snapshot == resultsLoader.loadNumIdentifiedPeptides()

def test_loadExperimentSummary(resultsLoader, snapshot_pandas):
    assert snapshot_pandas == resultsLoader.loadExperimentSummary()

def test_loadQuantificationMatrix(resultsLoader, snapshot_pandas):
    assert snapshot_pandas == resultsLoader.loadQuantificationMatrix()

def test_computeCV(resultsLoader, snapshot_pandas):
    assert snapshot_pandas == resultsLoader.computeCV()

def test_flattenDict():
    arg_in = {'a': {'a1': 1, 'a2': 2}, 'b': {'b1' : 1, 'b2': 2} }
    arg_out = ResultsLoader._flattenDict(arg_in)
    print(arg_out)
    assert arg_out == {'a1 (a)': 1, 'a2 (a)': 2, 'b1 (b)': 1, 'b2 (b)': 2}

'''
def test_plotIdentifications(resultsLoader, snapshot_bokeh):
    assert snapshot_bokeh == resultsLoader.plotIdentifications()

def test_plotQuantification(resultsLoader, snapshot_bokeh):
    assert snapshot_bokeh == resultsLoader.plotQuantification()

def test_plotCV(resultsLoader, snapshot_bokeh):
    assert snapshot_bokeh == resultsLoader.plotCV()

def test_plotUpset(resultsLoader, snapshot_bokeh):
    assert snapshot_bokeh == resultsLoader.plotUpset()
'''


