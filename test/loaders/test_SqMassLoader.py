"""
test/loaders/test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import SqMassLoader
from massdash.util import find_git_directory
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def loader():
    return SqMassLoader(dataFiles=[f'{str(TEST_PATH)}/test_data/xics/test_chrom_1.sqMass', f'{str(TEST_PATH)}/test_data/xics/test_chrom_2.sqMass'], rsltsFile=f"{str(TEST_PATH)}/test_data/osw/test_data.osw")

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.mark.parametrize('fullpeptidename,charge', [('NKESPT(UniMod:21)KAIVR(UniMod:267)', 3), ('INVALID', 0)])
def test_loadTransitionGroupFeature(loader, fullpeptidename, charge, snapshot):
    # Test loading a peak feature for a valid peptide ID and charge
    peak_feature = loader.loadTransitionGroupFeatures(fullpeptidename, charge)
    assert snapshot == AmberDataSerializer.serialize(peak_feature)

@pytest.mark.parametrize('fullpeptidename,charge', [('NKESPT(UniMod:21)KAIVR(UniMod:267)', 3), ('INVALID', 0)])
def test_loadTransitionGroups(loader, fullpeptidename, charge, snapshot):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroups(fullpeptidename, charge) 
    assert snapshot == AmberDataSerializer.serialize(transitionGroup)

@pytest.mark.parametrize('fullpeptidename,charge', [('NKESPT(UniMod:21)KAIVR(UniMod:267)', 3), ('INVALID', 0)])
def test_loadTransitionGroupsDf(loader, fullpeptidename, charge, snapshot_pandas):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroupsDf(fullpeptidename, charge) 
    assert snapshot_pandas == transitionGroup 

@pytest.mark.parametrize('fullpeptidename,charge', [('NKESPT(UniMod:21)KAIVR(UniMod:267)', 3), ('INVALID', 0)])
def test_loadTransitionGroupFeaturesDf(loader, fullpeptidename, charge, snapshot_pandas):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroupFeaturesDf(fullpeptidename, charge)
    assert snapshot_pandas == transitionGroup