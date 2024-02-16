import unittest
from massdash.loaders.access.TransitionPQPDataAccess import TransitionPQPDataAccess
from snapshottest import TestCase

class TestTransitionPQPDataAccess(TestCase):
    def setUp(self):
        self.filename = "../../test_data/example_dia/openswath/lib/test.pqp"
        self.data_access = TransitionPQPDataAccess(self.filename)
    
    def tearDown(self):
        self.data_access.close()
    
 
    def test_getTransitionList(self):
        # test getTransitionList() method
        transitions = self.data_access.getTransitionList()
        self.assert_match_snapshot(transitions)

    def test_validate_columns(self):
        # test _validate_columns() method
        self.data_access.data = self.data_access.getTransitionList()
        self.assertTrue(self.data_access._validate_columns())
    
    def test_load(self):
        # test load() method
        self.data_access.load()
        self.assertMatchSnapshot(self.data_access.data)

    def test_empty(self):
        # test empty() method
        self.data_access.load()
        self.assertFalse(self.data_access.empty())

if __name__ == '__main__':
    unittest.main()
