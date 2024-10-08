"""
test/loaders/test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import SqMassLoader
from massdash.util import find_git_directory
from massdash.testing import PandasSnapshotExtension

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data' / 'example_dia'

@pytest.fixture(params=['openswath', 'combined'])
def loader(request):
    dataFiles = ['test_raw_1.sqMass', 'test_raw_2.sqMass']
    dataFiles = [ str(TEST_PATH / 'openswath' / 'xics' / f) for f in dataFiles ]

    if request.param == 'openswath':
        return SqMassLoader(dataFiles=dataFiles, rsltsFile=str(TEST_PATH / 'openswath' / 'osw' / "test.osw"))
    if request.param == 'combined':
        return SqMassLoader(dataFiles=dataFiles, 
                            rsltsFile=[str(TEST_PATH / 'openswath' / 'osw' / "test.osw"), 
                                       str(TEST_PATH / 'diann' / 'report' / "test_diann_report_combined.tsv")])

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

def test_init_error():
    # if no .osw file is provided then throw an error because .sqMass file cannot be indexed
    with pytest.raises(ValueError):
        SqMassLoader(rsltsFile=f"{TEST_PATH}/diann/report/test_diann_report_combined.tsv", dataFiles=f'{TEST_PATH}/openswath/xics/test_raw_1.mzML')

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_loadTransitionGroupFeature(loader, fullpeptidename, charge, snapshot):
    # Test loading a peak feature for a valid peptide ID and charge
    peak_feature = loader.loadTransitionGroupFeatures(fullpeptidename, charge)
    assert snapshot == AmberDataSerializer.serialize(peak_feature)

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_loadTransitionGroups(loader, fullpeptidename, charge, snapshot):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroups(fullpeptidename, charge) 
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