"""
tests/loaders/test_OSWDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from snapshottest import TestCase
import pandas as pd
from massdash.loaders.access.OSWDataAccess import OSWDataAccess
from massdash.structs.TransitionGroup import TransitionGroup
import numpy as np

class TestOSWDataAccess(TestCase):
    def setUp(self):
        self.db_path = "../test_data/osw/test_data.osw"
        self.osw_data_access = OSWDataAccess(self.db_path)

    def test_getProteinTable(self):
        protein_table = self.osw_data_access.getProteinTable()
        self.assertIsInstance(protein_table, pd.DataFrame)
        self.assertMatchSnapshot(protein_table.shape)
        self.assertMatchSnapshot(protein_table)

    def test_getPeptideTable(self):
        peptide_table = self.osw_data_access.getPeptideTable()
        self.assertIsInstance(peptide_table, pd.DataFrame)
        self.assertMatchSnapshot(peptide_table.shape)
        self.assertMatchSnapshot(peptide_table)

    def test_getPeptideTableFromProteinID(self):
        protein_id = 539
        peptide_table = self.osw_data_access.getPeptideTableFromProteinID(protein_id)
        self.assertIsInstance(peptide_table, pd.DataFrame)
        self.assertMatchSnapshot(peptide_table.shape)
        self.assertMatchSnapshot(peptide_table)

    def test_getPrecursorCharges(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        precursor_charges = self.osw_data_access.getPrecursorCharges(fullpeptidename)
        self.assertIsInstance(precursor_charges, pd.DataFrame)
        self.assertMatchSnapshot(precursor_charges.shape)
        self.assertMatchSnapshot(precursor_charges)

    def test_getPeptideTransitionInfo(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        peptide_transition_info = self.osw_data_access.getPeptideTransitionInfo(fullpeptidename, charge)
        self.assertIsInstance(peptide_transition_info, pd.DataFrame)
        self.assertMatchSnapshot(peptide_transition_info.shape)
        self.assertMatchSnapshot(peptide_transition_info)
    
    def test_getPrecursorIDFromPeptideAndCharge(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        precursor_id = self.osw_data_access.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        self.assertIsInstance(precursor_id, np.int64)
        self.assertMatchSnapshot(precursor_id)

        ## test invalid
        fullpeptidename = "INVALID"
        charge = 0
        precursor_id = self.osw_data_access.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        self.assertIsNone(precursor_id)
    
    def test_getTransitionIDAnnotationFromSequence(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        transition_group_feature = self.osw_data_access.getTransitionIDAnnotationFromSequence(fullpeptidename, charge)
        self.assertIsInstance(transition_group_feature, pd.DataFrame)
        self.assertMatchSnapshot(transition_group_feature.shape)
        self.assertMatchSnapshot(transition_group_feature)

        ## test invalid
        fullpeptidename = "INVALID"
        charge = 0
        transition_group_feature = self.osw_data_access.getTransitionIDAnnotationFromSequence(fullpeptidename, charge)
        self.assertIsInstance(transition_group_feature, pd.DataFrame)

    def test_getTransitionGroupFeatures(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        run = "test_chrom_1"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeatures(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, list)
        self.assertMatchSnapshot(len(transition_group_feature))
        self.assertMatchSnapshot(transition_group_feature)

        ## test invalid peptide
        fullpeptidename = "INVALID"
        charge = 0
        run = "test_chrom_1"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeatures(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, list)
        self.assertMatchSnapshot(len(transition_group_feature))

        ## test invalid run 
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        run = "INVALID"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeatures(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, list)
        self.assertMatchSnapshot(len(transition_group_feature))
    
    def test_getTransitionGroupFeaturesDf(self):
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        run = "test_chrom_1"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeaturesDf(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, pd.DataFrame)
        self.assertMatchSnapshot(transition_group_feature.shape)
        self.assertMatchSnapshot(transition_group_feature)

        ## test invalid peptide
        fullpeptidename = "INVALID"
        charge = 0
        run = "test_chrom_1"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeaturesDf(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, pd.DataFrame)
        self.assertMatchSnapshot(transition_group_feature.empty)

        ## test invalid run 
        fullpeptidename = "ANS(UniMod:21)SPTTNIDHLK(UniMod:259)"
        charge = 2
        run = "INVALID"
        transition_group_feature = self.osw_data_access.getTransitionGroupFeaturesDf(fullpeptidename, charge, run)
        self.assertIsInstance(transition_group_feature, pd.DataFrame)
        self.assertMatchSnapshot(transition_group_feature.empty)
    
    def tearDown(self):
        self.osw_data_access.conn.close()

if __name__ == '__main__':
    unittest.main()