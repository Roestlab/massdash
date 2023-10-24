import unittest
from snapshottest import TestCase
import pandas as pd
from massseer.SqlDataAccess import OSWDataAccess, SqMassDataAccess

class TestOSWDataAccess(TestCase):
    def setUp(self):
        self.db_path = "test_data/osw/test_data.osw"
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


class TestSqMassDataAccess(TestCase):
    def setUp(self):
        self.db_path = "test_data/xics/test_chrom_1.sqMass"
        self.mass_data_access = SqMassDataAccess(self.db_path)

    def test_getPrecursorChromIDs(self):
        precursor_id = 30
        chrom_ids = self.mass_data_access.getPrecursorChromIDs(precursor_id)["chrom_ids"]
        self.assertMatchSnapshot(chrom_ids)

    def test_getDataForChromatograms(self):
        ids = [41353, 41354, 41387]
        data = self.mass_data_access.getDataForChromatograms(ids)
        self.assertMatchSnapshot(len(data))
        self.assertIsInstance(data[0][0], list)
        self.assertIsInstance(data[0][1], list)

    def test_getDataForChromatogram(self):
        myid = 424
        data = self.mass_data_access.getDataForChromatogram(myid)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)

    def test_getDataForChromatogramFromNativeId(self):
        native_id = 992928
        data = self.mass_data_access.getDataForChromatogramFromNativeId(native_id)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)

    def test_getDataForChromatogramsFromNativeIds(self):
        native_ids = [180, 181, 182, 183, 183, 185]
        data = self.mass_data_access.getDataForChromatogramsFromNativeIds(native_ids)
        self.assertMatchSnapshot(len(data))
        self.assertIsInstance(data[0][0], list)
        self.assertIsInstance(data[0][1], list)

    def tearDown(self):
        self.mass_data_access.conn.close()