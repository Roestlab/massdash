import unittest
from massdash.loaders.access.TransitionTSVDataAccess import TransitionTSVDataAccess
from snapshottest import TestCase
import pandas as pd

class TestTransitionTSVDataAccess(TestCase):

    def setUp(self):
        self.filename = "../../test_data/example_dia/diann/lib/test_1_lib.tsv"
        self.data_access = TransitionTSVDataAccess(self.filename)

    def test_resolve_column_names(self):
        # Test for _resolve_column_names() method
        data_access = TransitionTSVDataAccess(self.filename)
        data_access.data = pd.read_csv(self.filename, sep='\t')
        data_access._resolve_column_names()
        self.assert_match_snapshot(data_access.data)
     
    def test_generate_annotation(self):
        # Test for _generate_annotation() method
        data_access = TransitionTSVDataAccess(self.filename)
        data_access.data = pd.read_csv(self.filename, sep='\t')
        data_access._resolve_column_names()
        data_access.generate_annotation()
        self.assert_match_snapshot(data_access.data['Annotation'])

    def test_validate_columns(self):
        # Test for _validate_columns() method
        data_access = TransitionTSVDataAccess(self.filename)
        data_access.data = pd.read_csv(self.filename, sep='\t')
        data_access._resolve_column_names()
        data_access.generate_annotation()
        data_access._validate_columns()
        #missing_columns = set(TransitionTSVDataAccess.REQUIRED_TSV_COLUMNS).difference(set(data_access.data.columns))
        self.assertTrue(data_access._validate_columns())
   
    def test_load(self):
        self.data_access.load()
        self.assertMatchSnapshot(self.data_access.data)
   
    def test_empty(self):
        # Test if the data is empty
        self.data_access.load()
        self.assertFalse(self.data_access.empty())


if __name__ == '__main__':
    unittest.main()
