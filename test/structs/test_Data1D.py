"""
test/structs/test_Data1D
~~~~~~~~~~~~~~~~~~~~~~~~
"""


import unittest
import numpy as np
import pandas as pd
from massdash.structs.Data1D import Data1D

class DummyData1D(Data1D):
    def toPandasDf(self) -> pd.DataFrame:
        # Your implementation here (can be a dummy implementation for testing)
        return pd.DataFrame({'Data': self.data, 'Intensity': self.intensity})

class TestData1D(unittest.TestCase):
    def test_empty(self):
        # Test case 1: both data and intensity are empty
        data = np.array([])
        intensity = np.array([])
        obj = DummyData1D(data, intensity)
        self.assertTrue(obj.empty())

        # Test case 2: data is not empty, intensity is empty
        data = np.array([1, 2, 3])
        intensity = np.array([])
        obj = DummyData1D(data, intensity)
        self.assertTrue(obj.empty())

        # Test case 3: data is empty, intensity is not empty
        data = np.array([])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        self.assertTrue(obj.empty())

        # Test case 4: both data and intensity are not empty
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        self.assertFalse(obj.empty())

    def test_max_without_boundary(self):
        # Test case 1: Maximum intensity without boundary
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        result = obj.max()
        self.assertEqual(result, (3, 0.9))

        # Test case 2: Maximum intensity without boundary (multiple maximum values)
        data = np.array([1, 2, 3, 4])
        intensity = np.array([0.5, 0.8, 0.9, 0.9])
        obj = DummyData1D(data, intensity)
        result = obj.max()
        self.assertEqual(result, (3, 0.9))

    def test_max_with_boundary(self):
        # Test case 1: Maximum intensity within boundary
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        result = obj.max((2, 4))
        self.assertEqual(result, (3, 0.9))

        # Test case 2: Maximum intensity within boundary (multiple maximum values)
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.9, 0.6])
        obj = DummyData1D(data, intensity)
        result = obj.max((2, 4))
        self.assertEqual(result, (3, 0.9))
        
    def test_filter(self):
        # Test case 1: Filter within boundary
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        filtered_obj = obj.filter((2, 4))
        self.assertTrue(np.array_equal(filtered_obj.data, np.array([2, 3, 4])))
        self.assertTrue(np.array_equal(filtered_obj.intensity, np.array([0.8, 0.9, 0.7])))

        # Test case 2: Filter with non-tuple boundary
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        with self.assertRaises(ValueError):
            obj.filter(2)

    def test_sum_without_boundary(self):
        # Test case 1: Sum of all intensities without boundary
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        result = obj.sum()
        self.assertEqual(result, 2.2)

        # Test case 2: Sum of all intensities without boundary (empty data)
        data = np.array([])
        intensity = np.array([])
        obj = DummyData1D(data, intensity)
        result = obj.sum()
        self.assertEqual(result, 0.0)

    def test_sum_with_boundary(self):
        # Test case 1: Sum of intensities within boundary
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        result = obj.sum((2, 4))
        self.assertAlmostEqual(result, 2.4)

        # Test case 2: Sum of intensities within boundary (empty data)
        data = np.array([])
        intensity = np.array([])
        obj = DummyData1D(data, intensity)
        result = obj.sum((2, 4))
        self.assertEqual(result, 0.0)
        
    def test_median_without_boundary(self):
        # Test case 1: Median intensity without boundary
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        result = obj.median()
        self.assertEqual(result, 0.8)

    def test_median_with_boundary(self):
        # Test case 1: Median intensity within boundary
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        result = obj.median((2, 4))
        self.assertEqual(result, 0.8)

    def test_adjust_length(self):
        # Test case 1: length is equal to current length
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        new_data, new_intensity = obj.adjust_length(3)
        self.assertTrue(np.array_equal(new_data, data))
        self.assertTrue(np.array_equal(new_intensity, intensity))

        # Test case 2: length is smaller than current length
        data = np.array([1, 2, 3, 4, 5])
        intensity = np.array([0.5, 0.8, 0.9, 0.7, 0.6])
        obj = DummyData1D(data, intensity)
        new_data, new_intensity = obj.adjust_length(3)
        self.assertTrue(np.array_equal(new_data, np.array([2, 3, 4])))
        self.assertTrue(np.array_equal(new_intensity, np.array([0.8, 0.9, 0.7])))

        # Test case 3: length is larger than current length (even length difference)
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        new_data, new_intensity = obj.adjust_length(7)
        self.assertTrue(np.array_equal(new_data, np.array([-1, 0, 1, 2, 3, 4, 5])))
        self.assertTrue(np.array_equal(new_intensity, np.array([0, 0, 0.5, 0.8, 0.9, 0, 0])))

        # Test case 4: length is larger than current length (odd length difference)
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        new_data, new_intensity = obj.adjust_length(6)
        self.assertTrue(np.array_equal(new_data, np.array([-1, 0, 1, 2, 3, 4])))
        self.assertTrue(np.array_equal(new_intensity, np.array([0, 0, 0.5, 0.8, 0.9, 0])))

        # Test case 5: length is larger than current length (unequal paddings)
        data = np.array([1, 2, 3])
        intensity = np.array([0.5, 0.8, 0.9])
        obj = DummyData1D(data, intensity)
        new_data, new_intensity = obj.adjust_length(5)
        self.assertTrue(np.array_equal(new_data, np.array([0, 1, 2, 3, 4])))
        self.assertTrue(np.array_equal(new_intensity, np.array([0, 0.5, 0.8, 0.9, 0])))


if __name__ == '__main__':
    unittest.main()