"""
test/structs/test_TransitionGroupCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from massdash.structs import TransitionGroup, Chromatogram
from massdash.structs.TransitionGroupCollection import TransitionGroupCollection
import pandas as pd

class TestTransitionGroupCollection(unittest.TestCase):

    def setUp(self):
        # Create some example chromatograms for testing
        self.precursorChroms1 = [Chromatogram([1, 2, 3], [4, 5, 6], label='test1'), Chromatogram([1, 2, 3], [7, 8, 9], label='test2')]
        self.transitionChroms1 = [Chromatogram([1, 2, 3], [10, 11, 12], label='test3'), Chromatogram([1, 2, 3], [13, 14, 15], label='test4')]

        self.precursorChroms2 = [Chromatogram([1, 2, 3], [4.1, 5.1, 6.1], label='test1'), Chromatogram([1, 2, 3], [7.1, 8.1, 9.1], label='test2')]
        self.transitionChroms2 = [Chromatogram([1, 2, 3], [10.1, 11.1, 12.1], label='test3'), Chromatogram([1, 2, 3], [13.1, 14.1, 15.1], label='test4')]

        self.transitionGroup1 = TransitionGroup(self.precursorChroms1, self.transitionChroms1)
        self.transitionGroup2 = TransitionGroup(self.precursorChroms2, self.transitionChroms2)

        self.transitionGroupCollection = TransitionGroupCollection({'run1': self.transitionGroup1, 'run2': self.transitionGroup2})

    def test_toPandasDf(self):
        # Test the toPandasDf() method
        df = self.transitionGroupCollection.toPandasDf()
        expected = pd.DataFrame({'rt': [1.0,2.0,3.0] * 8, 'intensity': [4,5,6,7,8,9,10,11,12,13,14,15] + [4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1, 12.1, 13.1, 14.1, 15.1], 'annotation': ['test1', 'test1', 'test1', 'test2', 'test2', 'test2', 'test3', 'test3', 'test3', 'test4', 'test4', 'test4'] * 2, 'run': ['run1'] * 12 + ['run2'] * 12})
        pd.testing.assert_frame_equal(df.reset_index(drop=True), expected.reset_index(drop=True))