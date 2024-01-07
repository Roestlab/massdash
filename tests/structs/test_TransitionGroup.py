"""
tests/structs/test_TransitionGroup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from massdash.structs.TransitionGroup import TransitionGroup
from massdash.structs.Chromatogram import Chromatogram
import numpy as np

class TestTransitionGroup(unittest.TestCase):

    def setUp(self):
        # Create some example chromatograms for testing
        self.precursorChroms = [Chromatogram([1, 2, 3], [4, 5, 6], label='test1'), Chromatogram([1, 2, 3], [7, 8, 9], label='test2')]
        self.transitionChroms = [Chromatogram([1, 2, 3], [10, 11, 12], label='test3'), Chromatogram([1, 2, 3], [13, 14, 15], label='test4')]
        self.transitionGroup = TransitionGroup(self.precursorChroms, self.transitionChroms)

    def test_max(self):
        # Test the max() method with some example boundaries
        self.assertAlmostEqual(self.transitionGroup.max((1.5, 2.5), level='ms2'), 14.0)
        self.assertAlmostEqual(self.transitionGroup.max((2.5, 3.5), level='ms2'), 15.0)
        self.assertAlmostEqual(self.transitionGroup.max((1.5, 2.5), level='ms1ms2'), 14.0)
        self.assertAlmostEqual(self.transitionGroup.max((2.5, 3.5), level='ms2'), 15.0)

    def test_sum(self):
        # Test the sum() method with some example boundaries
        self.assertAlmostEqual(self.transitionGroup.sum((1.5, 2.5), level='ms2'), 11 + 14)
        self.assertAlmostEqual(self.transitionGroup.sum((2.5, 3.5), level='ms2'), 12 + 15)
        self.assertAlmostEqual(self.transitionGroup.sum((1.5, 2.5), level='ms1ms2'), 5 + 8 + 11 + 14)
        self.assertAlmostEqual(self.transitionGroup.sum((2.5, 3.5), level='ms1ms2'), 6 + 9 +12 + 15)

    def test_flatten(self):
        # Test the flatten() method
        flattened = self.transitionGroup.flatten(level='ms2')
        np.array_equal(flattened.data, np.array([1, 2, 3, 1, 2, 3]))
        np.array_equal(flattened.intensity, [10, 11, 12, 13, 14, 15])
        flattened = self.transitionGroup.flatten(level='ms1ms2')
        np.array_equal(flattened.data, np.array([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]))
        np.array_equal(flattened.intensity, np.array([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ,15]))

    def test_median(self):
        # Test the median() method with some example boundaries
        self.assertAlmostEqual(self.transitionGroup.median((1.5, 2.5), level='ms2'), 12.5)
        self.assertAlmostEqual(self.transitionGroup.median((2.5, 3.5), level='ms2'), 13.5)
        self.assertAlmostEqual(self.transitionGroup.median((1.5, 2.5), level='ms1ms2'), np.median(np.array([5,8,11,14])))
        self.assertAlmostEqual(self.transitionGroup.median((2.5, 3.5), level='ms1ms2'), np.median(np.array([6, 9, 12, 15])))

if __name__ == '__main__':
    unittest.main()
