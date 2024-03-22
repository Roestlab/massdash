"""
test/loaders/access/test_OSWDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest
from pathlib import Path
import pandas as pd

from massdash.testing import PandasSnapshotExtension
from massdash.loaders.access.OSWDataAccess import OSWDataAccess
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.fixture
def osw_data_access():
    db_path = f"{str(TEST_PATH)}/test_data/osw/ionMobilityTest.osw"
    osw_data_access = OSWDataAccess(db_path)
    yield osw_data_access
    osw_data_access.conn.close()

@pytest.fixture
def osw_data_access2():
    db_path = f"{str(TEST_PATH)}/test_data/osw/ionMobilityTest.osw"
    osw_data_access = OSWDataAccess(db_path)
    yield osw_data_access
    osw_data_access.conn.close()


@pytest.fixture(params=['ionMobilityTest2', None])
def run(request):
    return request.param

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

@pytest.mark.parametrize("fullpeptidename,charge", [("AFVDFLSDEIK", 2), ("INVALID", 0)])
def test_getTransitionIDAnnotationFromSequence(osw_data_access, snapshot_pandas, fullpeptidename, charge):
    transition_group_feature = osw_data_access.getTransitionIDAnnotationFromSequence(fullpeptidename, charge)
    assert snapshot_pandas == transition_group_feature 

@pytest.mark.parametrize("fullpeptidename,charge", [("AFVDFLSDEIK", 2), ("INVALID", 0)])
def test_getPrecursorIDFromPeptideAndCharge(osw_data_access, snapshot, fullpeptidename, charge):
    precursor_id = osw_data_access.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
    assert snapshot == precursor_id 

@pytest.mark.parametrize("fullpeptidename,charge,run", [("AFVDFLSDEIK", 2, 'ionMobilityTest2'), ("INVALID", 0, 'ionMobilityTest2'), ("AFVDFLSDEIK", 2, 'INVALID'),])
def test_getTransitionGroupFeatures(osw_data_access, snapshot, fullpeptidename, charge, run):
    transition_group_feature = osw_data_access.getTransitionGroupFeatures(run, fullpeptidename, charge)
    print(transition_group_feature)
    assert snapshot == transition_group_feature

@pytest.mark.parametrize("fullpeptidename,charge,run", [("AFVDFLSDEIK", 2, 'ionMobilityTest2'), ("INVALID", 0, 'ionMobilityTest2'), ("AFVDFLSDEIK", 2, 'INVALID')])
def test_getTransitionGroupFeaturesDf(osw_data_access, snapshot_pandas, run, fullpeptidename, charge):
    transition_group_feature = osw_data_access.getTransitionGroupFeaturesDf(run, fullpeptidename, charge)
    assert snapshot_pandas == transition_group_feature

def test_getRunNames(osw_data_access, snapshot):
    runnames = osw_data_access.getRunNames()
    assert snapshot == runnames 

def test_getIdentifiedPrecursors(osw_data_access, snapshot):
    precursors = osw_data_access.getIdentifiedPrecursors()
    assert precursors == snapshot

def test_getIdentifiedPrecursorIntensities(osw_data_access, run, snapshot_pandas):
    intensities = osw_data_access.getIdentifiedPrecursorIntensities(run=run)
    assert snapshot_pandas == intensities

def test_getIdentifiedProteins(osw_data_access, run, snapshot):
    proteins = osw_data_access.getIdentifiedProteins(run=run)
    assert proteins == snapshot

def test_getIdentifiedPeptides(osw_data_access, run, snapshot):
    peptides = osw_data_access.getIdentifiedPeptides(run=run)
    assert peptides == snapshot

def test_getNumIdentifiedPrecursors(osw_data_access, run, snapshot):
    num_precursors = osw_data_access.getNumIdentifiedPrecursors(run=run)
    assert num_precursors == snapshot

def test_getNumIdentifiedProteins(osw_data_access, run, snapshot):
    num_proteins = osw_data_access.getNumIdentifiedProteins(run=run)
    assert num_proteins == snapshot

def test_getNumIdentifiedPeptides(osw_data_access, run, snapshot):
    num_peptides = osw_data_access.getNumIdentifiedPeptides(run=run)
    assert num_peptides == snapshot

def test_getSoftware(osw_data_access):
    assert osw_data_access.getSoftware() == "OpenSWATH"

def test_getExperimentSummary(osw_data_access, snapshot_pandas):
    experiment_summary = osw_data_access.getExperimentSummary()
    assert snapshot_pandas == experiment_summary

def test_initializeValidScores(osw_data_access2, snapshot):
    # Open test.osw file because has full .osw output unlike ion mobility
    osw_data_access2._initializeValidScores()

    assert snapshot == osw_data_access2.validScores

@pytest.mark.parametrize("score_table,score,context", [("SCORE_MS2", "SCORE", None),
                                                       ("FEATURE_MS2", "VAR_XCORR_COELUTION", None),
                                                       ("FEATURE_MS1", "VAR_XCORR_COELUTION_COMBINED", None),
                                                       ("SCORE_PROTEIN", "SCORE", "global"),
                                                       ("SCORE_PROTEIN", "SCORE", "run-specific"),
                                                       ("SCORE_PROTEIN", "SCORE", "experiment-wide"),
                                                       ("SCORE_PEPTIDE", "SCORE", "global"),
                                                       ("SCORE_PEPTIDE", "SCORE", "run-specific"),
                                                       ("SCORE_PEPTIDE", "SCORE", "experiment-wide")])
def test_getScoreTable(osw_data_access2, score_table, score, context, snapshot_pandas):
    df = osw_data_access2.getScoreTable(score_table, score, context)
    assert snapshot_pandas == df





def test_getCV():

    pass
