"""
test/loaders/access/test_SqMassDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
import pandas as pd

from massdash.loaders.access.SqMassDataAccess import SqMassDataAccess
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def mass_data_access():
    db_path = f"{str(TEST_PATH)}/test_data/xics/test_chrom_1.sqMass"
    mass_data_access = SqMassDataAccess(db_path)
    yield mass_data_access
    mass_data_access.conn.close()

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)


def test_getPrecursorChromIDs(mass_data_access, snapshot):
    precursor_id = 30
    chrom_ids = mass_data_access.getPrecursorChromIDs(precursor_id)
    assert snapshot == chrom_ids

def test_getDataForChromatograms(mass_data_access, snapshot_pandas):
    ids = [41353, 41354, 41387]
    annots = ["y4^1", "y3^1", "y6^1"]
    data = mass_data_access.getDataForChromatograms(ids, annots)
    assert len(data) == 3

    # assemble the data into snapshot
    data_out = pd.concat([d.toPandasDf() for d in data]) 
    assert snapshot_pandas == data_out

def test_getDataForChromatogram(mass_data_access, snapshot_pandas):
    myid = 424
    data = mass_data_access.getDataForChromatogram(myid, "y4^1")
    data_out = data.toPandasDf()
    assert snapshot_pandas == data_out

def test_getDataForChromatogramFromNativeId(mass_data_access, snapshot_pandas):
    native_id = 992928
    data = mass_data_access.getDataForChromatogramFromNativeId(native_id)
    data_out = pd.DataFrame(data)
    assert snapshot_pandas == data_out

def test_getDataForChromatogramsFromNativeIds(mass_data_access, snapshot_pandas):
    native_ids = [180, 181, 182, 183, 183, 185]
    labels = ["y4^1", "y3^1", "y6^1", "y7^1", "y7^1", "y8^1"]
    data = mass_data_access.getDataForChromatogramsFromNativeIds(native_ids, labels)
    data_out = pd.concat([d.toPandasDf() for d in data])
    assert snapshot_pandas == data_out

@pytest.mark.parametrize("ids,labels", [([41353, 41354, 41387], ["y4^1", "y3^1", "y6^1"]), ([0], ["y4^1"]), ([], ["y4^1"])])
def test_getDataForChromatogramsDf(mass_data_access, snapshot_pandas, ids, labels):
    # Assuming you have some data to test this method
    df = mass_data_access.getDataForChromatogramsDf(ids, labels)
    assert snapshot_pandas == df

def test_getDataForChromatogramsFromNativeIdsDf(mass_data_access, snapshot_pandas):
    ids = [180, 181, 182, 183, 183, 185]
    labels = ["y4^1", "y3^1", "y6^1", "y7^1", "y7^1", "y8^1"]
    data = mass_data_access.getDataForChromatogramsFromNativeIdsDf(ids, labels)
    assert snapshot_pandas == data