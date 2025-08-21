"""
test/loaders/access/test_SqMassDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
import pandas as pd
from syrupy.extensions.amber import AmberDataSerializer

from massdash.loaders.access.OpenSwathXICParquetAccess import OpenSwathXICParquetAccess
from massdash.testing import PandasSnapshotExtension
from massdash.util import find_git_directory


TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data' / 'example_dia'

@pytest.fixture
def parquet_data_access():
    db_path = f"{str(TEST_PATH)}/openswath/xics/test_raw_1.parquet"
    mass_data_access = OpenSwathXICParquetAccess(db_path)
    yield mass_data_access

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_getChromatogramsFromSequenceAndCharge(parquet_data_access, snapshot, fullpeptidename, charge):
    data = parquet_data_access.getChromatogramsFromSequenceAndCharge(fullpeptidename, charge)
    assert snapshot == AmberDataSerializer.serialize(data)

@pytest.mark.parametrize('fullpeptidename,charge', [('AGAANIVPNSTGAAK', 3), ('INVALID', 0)])
def test_getChromatogramDfFromSequenceAndCharge(parquet_data_access, snapshot_pandas, fullpeptidename, charge):
    data = parquet_data_access.getChromatogramDfFromSequenceAndCharge(fullpeptidename, charge)
    assert snapshot_pandas == data
