"""
test/loaders/test_SqMassDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from pathlib import Path

import pandas as pd
from snapshottest import TestCase

from massdash.loaders.access.SqMassDataAccess import SqMassDataAccess
from massdash.structs.Chromatogram import Chromatogram
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'


class TestSqMassDataAccess(TestCase):
    def setUp(self):
        self.db_path = f"{str(TEST_PATH)}/test_data/xics/test_chrom_1.sqMass"
        self.mass_data_access = SqMassDataAccess(self.db_path)

    def test_getPrecursorChromIDs(self):
        precursor_id = 30
        chrom_ids = self.mass_data_access.getPrecursorChromIDs(precursor_id)["chrom_ids"]
        self.assertMatchSnapshot(chrom_ids)

    def test_getDataForChromatograms(self):
        ids = [41353, 41354, 41387]
        data = self.mass_data_access.getDataForChromatograms(ids, ["y4^1", "y3^1", "y6^1"])
        self.assertMatchSnapshot(len(data))
        self.assertIsInstance(data[0], Chromatogram)
        self.assertIsInstance(data[1], Chromatogram)
        self.assertIsInstance(data[2], Chromatogram)

    def test_getDataForChromatogram(self):
        myid = 424
        data = self.mass_data_access.getDataForChromatogram(myid, "y4^1")
        self.assertIsInstance(data, Chromatogram)

    def test_getDataForChromatogramFromNativeId(self):
        native_id = 992928
        data = self.mass_data_access.getDataForChromatogramFromNativeId(native_id)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)

    def test_getDataForChromatogramsFromNativeIds(self):
        native_ids = [180, 181, 182, 183, 183, 185]
        labels = ["y4^1", "y3^1", "y6^1", "y7^1", "y7^1", "y8^1"]
        data = self.mass_data_access.getDataForChromatogramsFromNativeIds(native_ids, labels)
        self.assertMatchSnapshot(len(data))
        self.assertIsInstance(data[0], Chromatogram)
        self.assertIsInstance(data[1], Chromatogram)
        self.assertIsInstance(data[2], Chromatogram)
        self.assertMatchSnapshot(data)


    def test_getDataForChromatogramsDf(self):
        ids = [41353, 41354, 41387]
        data = self.mass_data_access.getDataForChromatogramsDf(ids, ["y4^1", "y3^1", "y6^1"])
        self.assertIsInstance(data, pd.DataFrame)
        self.assertMatchSnapshot(data)

        ## test invalid ids
        ids = [0]
        data = self.mass_data_access.getDataForChromatogramsDf(ids, ["y4^1"])
        self.assertIsInstance(data, pd.DataFrame)
        self.assert_match_snapshot(data)

        ## test empty ids
        ids = []
        data = self.mass_data_access.getDataForChromatogramsDf(ids, ["y4^1"])
        self.assertIsInstance(data, pd.DataFrame)
        self.assert_match_snapshot(data)

    def test_getDataForChromatogramsFromNativeIdsDf(self):
        ids = [180, 181, 182, 183, 183, 185]
        labels = ["y4^1", "y3^1", "y6^1", "y7^1", "y7^1", "y8^1"]
        data = self.mass_data_access.getDataForChromatogramsFromNativeIdsDf(ids, labels)
        self.assertIsInstance(data, pd.DataFrame)
        self.assert_match_snapshot(data)

    def tearDown(self):
        self.mass_data_access.conn.close()

if __name__ == '__main__':
    unittest.main()