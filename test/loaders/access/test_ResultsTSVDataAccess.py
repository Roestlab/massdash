import unittest
from massdash.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from snapshottest import TestCase

class TestResultsTSVDataAccess(TestCase):

    def setUp(self):
        self.access_diann = ResultsTSVDataAccess("../../test_data/example_dia/diann/report/test_1_diann_report.tsv", 'DIA-NN')
        #self.access_dream = ResultsTSVDataAccess("../../test_data/example_dia/dreamdia/test_dreamdia_report.tsv", 'DreamDIA')

        self.runname = 'test_raw_1'
        self.peptide = 'DYASIDAAPEER'
        self.charge = 2

    #### DIA-NN Access Tests ####
    def test_loadData_diann(self):
        # Test if the data is loaded correctly
        data = self.access_diann.loadData()
        self.assert_match_snapshot(data)

    def test_initializePeptideHashTable_diann(self):
        # Test if the peptide hash table is initialized correctly
        hash_table = self.access_diann._initializePeptideHashTable()
        self.assert_match_snapshot(hash_table)

    def test_getTopTransitionGroupFeature_diann(self):
        # Test if the top transition group feature is returned correctly
        feature = self.access_diann.getTopTransitionGroupFeature(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(feature)
    
    def test_getTransitionGroupFeatures_diann(self):
        # Test for getTransitionGroupFeatures() with DIA-NN input
        features = self.access_diann.getTransitionGroupFeatures(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(features)

    def test_getTransitionGroupFeaturesDf_diann(self):
        # Test for getTransitionGroupFeaturesDf() with DIA-NN input
        df = self.access_diann.getTransitionGroupFeaturesDf(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(df)

    def test_getTopTransitionGroupFeatureDf_diann(self):
        # Test for getTopTransitionGroupFeatureDf() with DIA-NN input
        df = self.access_diann.getTopTransitionGroupFeatureDf(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(df)
    

    def test_getExactRunName(self):
        # Test if the exact run name is returned correctly only tested for DIA-NN currently
        run_basename_wo_ext = "test_raw_1"
        exact_run_name = self.access_diann.getExactRunName(run_basename_wo_ext)
        self.assertIsInstance(exact_run_name, str)
        self.assertEqual(exact_run_name, "test_raw_1")
    
    
    
    ### DreamDIA Access Tests ###
    '''
    def test_loadData_dream(self):
        # Test if the data is loaded correctly
        data = self.access_dream.loadData()
        self.assert_match_snapshot(data)

    def test_initializePeptideHashTable_dream(self):
        # Test if the peptide hash table is initialized correctly
        hash_table = self.access_dream._initializePeptideHashTable()
        self.assert_match_snapshot(hash_table)

    def test_getTransitionGroupFeatures_dream(self):
        # Test for getTransitionGroupFeatures() with dreamDIA input
        features = self.access_dream.getTransitionGroupFeatures(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(features)

    def test_getTopTransitionGroupFeature_dream(self):
        # Test for getTopTransitionGroupFeature() with dreamDIA input
        feature = self.access_dream.getTopTransitionGroupFeature(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(feature)

    def test_getTransitionGroupFeaturesDf_dream(self):
        # Test for getTransitionGroupFeaturesDf() with dreamDIA input
        df = self.access_dream.getTransitionGroupFeaturesDf(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(df)

    def test_getTopTransitionGroupFeatureDf_dream(self):
        # Test for getTopTransitionGroupFeatureDf() with dreamDIA input
        df = self.access_dream.getTopTransitionGroupFeatureDf(self.runname, self.peptide, self.charge)
        self.assert_match_snapshot(df)
    '''

if __name__ == "__main__":
    unittest.main()
