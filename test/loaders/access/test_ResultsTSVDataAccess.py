"""
test/loaders/access/test_ResultsTSVDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import pytest
import pandas as pd
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

class MockResultsTSVDataAccess(ResultsTSVDataAccess):
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv(filename, sep='\t')

@pytest.fixture
def access(request):
    if request.param == 'diann':
        return ResultsTSVDataAccess(f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv", 'DIA-NN')
    if request.param == 'dream':
        return ResultsTSVDataAccess(f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv", 'DreamDIA')

@pytest.fixture
def mock_access(request):
    if request.param == 'DIA-NN':
        return MockResultsTSVDataAccess(f"{TEST_PATH}/test_data/example_dia/diann/report/test_1_diann_report.tsv")
    if request.param == 'DreamDIA':
        return MockResultsTSVDataAccess(f"{TEST_PATH}/test_data/example_dia/dreamdia/test_dreamdia_report.tsv")
    
@pytest.fixture
def runname():
    return 'test_raw_1'

@pytest.fixture
def peptide():
    return 'DYASIDAAPEER'

@pytest.fixture
def charge():
    return 2

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.mark.parametrize("mock_access", ['DIA-NN', 'DreamDIA'], indirect=True)
def test_loadData(mock_access, snapshot_pandas):
    mock_access.loadData()
    assert snapshot_pandas == mock_access.df

@pytest.mark.parametrize("access", ['diann', 'dream'], indirect=True)
def test_initializePeptideHashTable(access, snapshot_pandas):
    hash_table = access._initializePeptideHashTable()
    assert snapshot_pandas == hash_table

@pytest.mark.parametrize("mock_access,expected", [('DIA-NN', 'DIA-NN'), ('DreamDIA', 'DreamDIA')], indirect=['mock_access'])
def test_detectResultsType(mock_access, expected):
    assert mock_access.detectResultsType() == expected

@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTopTransitionGroupFeature(access, runname, peptide, charge, snapshot):
    feature = access.getTopTransitionGroupFeature(runname, peptide, charge)
    assert snapshot == AmberDataSerializer.object_as_named_tuple(feature)

@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTransitionGroupFeatures(access, runname, peptide, charge, snapshot):
    features = access.getTransitionGroupFeatures(runname, peptide, charge)
    assert snapshot == [ AmberDataSerializer.object_as_named_tuple(i) for i in features ]

@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTransitionGroupFeaturesDf(access, runname, peptide, charge, snapshot_pandas):
    df = access.getTransitionGroupFeaturesDf(runname, peptide, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize("access", ['diann'], indirect=['access'])
def test_getRunNames(access):
    runnames = access.getRunNames()
    assert runnames == ['test_raw_1']

@pytest.mark.parametrize("access", ['diann'], indirect=['access'])
def test_getIdentifiedPrecursors(access, snapshot):
    precursors = access.getIdentifiedPrecursors()
    assert precursors == snapshot

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getIdentifiedPrecursorIntensities(access, run, snapshot_pandas):
    intensities = access.getIdentifiedPrecursorIntensities(run=run)
    assert snapshot_pandas == intensities

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getIdentifiedProteins(access, run, snapshot):
    proteins = access.getIdentifiedProteins(run=run)
    assert proteins == snapshot

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getIdentifiedPeptides(access, run, snapshot):
    peptides = access.getIdentifiedPeptides(run=run)
    assert peptides == snapshot

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getNumIdentifiedPrecursors(access, run, snapshot):
    num_precursors = access.getNumIdentifiedPrecursors(run=run)
    assert num_precursors == snapshot

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getNumIdentifiedProteins(access, run, snapshot):
    num_proteins = access.getNumIdentifiedProteins(run=run)
    assert num_proteins == snapshot

@pytest.mark.parametrize("access,run", [('diann', 'test_raw_1'), ('diann', None)], indirect=['access'])
def test_getNumIdentifiedPeptides(access, run, snapshot):
    num_peptides = access.getNumIdentifiedPeptides(run=run)
    assert num_peptides == snapshot

@pytest.mark.parametrize("access,expected", [('diann', 'DIA-NN')], indirect=['access'])
def test_getSoftware(access, expected):
    assert access.getSoftware() == expected

@pytest.mark.parametrize("access", ['diann'], indirect=['access'])
def test_getExperimentSummary(access, snapshot_pandas):
    experiment_summary = access.getExperimentSummary()
    assert snapshot_pandas == experiment_summary

def test_getCV():
    pass