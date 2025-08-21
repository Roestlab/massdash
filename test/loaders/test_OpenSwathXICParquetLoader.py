"""
test/loaders/test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import OpenSwathXICParquetLoader
from massdash.util import find_git_directory
from massdash.testing import PandasSnapshotExtension

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data' / 'example_dia'

@pytest.fixture(params=['openswath', 'combined'])
def loader(request):
    dataFiles = ['test_raw_1.parquet', 'test_raw_2.parquet']
    dataFiles = [ str(TEST_PATH / 'openswath' / 'xics' / f) for f in dataFiles ]

    if request.param == 'openswath':
        return OpenSwathXICParquetLoader(dataFiles=dataFiles, rsltsFile=str(TEST_PATH / 'openswath' / 'osw' / "test.osw"))
    if request.param == 'combined':
        return OpenSwathXICParquetLoader(dataFiles=dataFiles, 
                            rsltsFile=[str(TEST_PATH / 'openswath' / 'osw' / "test.osw"), 
                                       str(TEST_PATH / 'diann' / 'report' / "test_diann_report_combined.tsv")])

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.mark.parametrize('fullpeptidename,charge,runNames', [('AGAANIVPNSTGAAK', 3, None), ('INVALID', 0, None), ('AGAANIVPNSTGAAK', 3, 'test_raw_1'), ('AGAANIVPNSTGAAK', 3, ['test_raw_1', 'test_raw_2'])])
def test_loadTransitionGroupFeature(loader, fullpeptidename, charge, runNames, snapshot):
    # Test loading a peak feature for a valid peptide ID and charge
    peak_feature = loader.loadTransitionGroupFeatures(fullpeptidename, charge, runNames=runNames)
    assert snapshot == AmberDataSerializer.serialize(peak_feature)

@pytest.mark.parametrize('fullpeptidename,charge,runNames', [('AGAANIVPNSTGAAK', 3, None), ('INVALID', 0, None), ('AGAANIVPNSTGAAK', 3, 'test_raw_1'), ('AGAANIVPNSTGAAK', 3, ['test_raw_1', 'test_raw_2'])])
def test_loadTransitionGroups(loader, fullpeptidename, charge, runNames, snapshot):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroups(fullpeptidename, charge, runNames=runNames) 
    print(transitionGroup)
    assert snapshot == AmberDataSerializer.serialize(transitionGroup)

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_loadTransitionGroupsDf(loader, fullpeptidename, charge, snapshot_pandas):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroupsDf(fullpeptidename, charge) 
    print(transitionGroup)
    assert snapshot_pandas == transitionGroup 

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_loadTransitionGroupFeaturesDf(loader, fullpeptidename, charge, snapshot_pandas):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroupFeaturesDf(fullpeptidename, charge)
    assert snapshot_pandas == transitionGroup