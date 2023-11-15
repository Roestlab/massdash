import unittest
from snapshottest import TestCase
import pandas as pd
from massseer.loaders.OSWDataAccess import OSWDataAccess

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

    def tearDown(self):
        self.osw_data_access.conn.close()

if __name__ == '__main__':
    unittest.main()