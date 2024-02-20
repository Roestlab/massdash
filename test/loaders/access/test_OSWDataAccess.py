"""
test/loaders/test_OSWDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
import pandas as pd

from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from massdash.loaders.access.OSWDataAccess import OSWDataAccess
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture
def osw_data_access():
    db_path = f"{str(TEST_PATH)}/test_data/osw/test_data.osw"
    osw_data_access = OSWDataAccess(db_path)
    yield osw_data_access
    osw_data_access.conn.close()

def test_getProteinTable(osw_data_access, snapshot_pandas):
    protein_table = osw_data_access.getProteinTable()
    assert snapshot_pandas == protein_table 

def test_getPeptideTable(osw_data_access, snapshot_pandas):
    peptide_table = osw_data_access.getPeptideTable()
    assert isinstance(peptide_table, pd.DataFrame)
    assert snapshot_pandas == peptide_table

def test_getPeptideTableFromProteinID(osw_data_access, snapshot_pandas):
    protein_id = 539
    peptide_table = osw_data_access.getPeptideTableFromProteinID(protein_id)
    assert snapshot_pandas == peptide_table

def test_getPrecursorCharges(osw_data_access, snapshot_pandas):
    fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
    precursor_charges = osw_data_access.getPrecursorCharges(fullpeptidename)
    assert snapshot_pandas == precursor_charges

def test_getPeptideTransitionInfo(osw_data_access, snapshot_pandas):
    fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
    charge = 2
    peptide_transition_info = osw_data_access.getPeptideTransitionInfo(fullpeptidename, charge)
    assert snapshot_pandas == peptide_transition_info 

@pytest.mark.parametrize("fullpeptidename,charge", [("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2), ("INVALID", 0)])
def test_getTransitionIDAnnotationFromSequence(osw_data_access, snapshot_pandas, fullpeptidename, charge):
    transition_group_feature = osw_data_access.getTransitionIDAnnotationFromSequence(fullpeptidename, charge)
    print(transition_group_feature)
    print(type(transition_group_feature))
    assert snapshot_pandas == transition_group_feature 

@pytest.mark.parametrize("fullpeptidename,charge", [("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2), ("INVALID", 0)])
def test_getPrecursorIDFromPeptideAndCharge(osw_data_access, snapshot, fullpeptidename, charge):
    precursor_id = osw_data_access.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
    assert snapshot == precursor_id 

@pytest.mark.parametrize("fullpeptidename,charge,run", [("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2, 'test_chrom_1'), ("INVALID", 0, 'test_chrom_1'), ("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2, 'INVALID'),])
def test_getTransitionGroupFeatures(osw_data_access, snapshot, fullpeptidename, charge, run):
    transition_group_feature = osw_data_access.getTransitionGroupFeatures(fullpeptidename, charge, run)
    assert snapshot == transition_group_feature


@pytest.mark.parametrize("fullpeptidename,charge,run", [("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2, 'test_chrom_1'), ("INVALID", 0, 'test_chrom_1'), ("ANS(UniMod:21)SPTTNIDHLK(UniMod:259)", 2, 'INVALID'),])
def test_getTransitionGroupFeaturesDf(osw_data_access, snapshot, fullpeptidename, charge, run):
    transition_group_feature = osw_data_access.getTransitionGroupFeaturesDf(fullpeptidename, charge, run)
    assert snapshot == transition_group_feature