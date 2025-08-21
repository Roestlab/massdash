"""
test/loaders/test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders import XICParquetDataLoader
from massdash.util import find_git_directory
from massdash.testing import PandasSnapshotExtension

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data' / 'diann'

@pytest.fixture
def loader():
    return XICParquetDataLoader(dataFiles=[str(TEST_PATH / 'diann_xic.parquet')], rsltsFile=str(TEST_PATH / 'diann_report_small_xic.tsv'))

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.mark.parametrize('fullpeptidename,charge,runNames', [('AAAAAAAAVPSAGPAGPAPTSAAGR', 2, None), ('INVALID', 0, None)])
def test_loadTransitionGroups(loader, fullpeptidename, charge, runNames, snapshot):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroups(fullpeptidename, charge, runNames=runNames) 
    assert snapshot == AmberDataSerializer.serialize(transitionGroup)

@pytest.mark.parametrize('fullpeptidename,charge', [('AAAAAAAAVPSAGPAGPAPTSAAGR', 2), ('INVALID', 0)])
def test_loadTransitionGroupsDf(loader, fullpeptidename, charge, snapshot_pandas):
    # Test loading a chromatogram for a valid peptide ID and charge
    transitionGroup = loader.loadTransitionGroupsDf(fullpeptidename, charge) 
    assert snapshot_pandas == transitionGroup 