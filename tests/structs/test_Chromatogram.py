
import unittest
import numpy as np
import pyopenms as po
from massseer.structs.Chromatogram import Chromatogram

class TestChromatogram(unittest.TestCase):
    def setUp(self):
        self.rt = np.array([1.0, 2.0, 3.0])
        self.intensity = np.array([10.0, 20.0, 30.0])
        self.label = "test"
        self.chromatogram = Chromatogram(self.rt, self.intensity, self.label)

    def test_str(self):
        self.assertEqual(f"{'-'*8} Chromatogram {'-'*8}\nlabel: {self.chromatogram.label}\nlength of chromatogram: {len(self.chromatogram.rt)}", str(self.chromatogram))

    def test_to_pyopenms(self):
        pyopenms_chromatogram = self.chromatogram.to_pyopenms()
        self.assertIsInstance(pyopenms_chromatogram, po.MSChromatogram)
        self.assertTrue(np.array_equal(pyopenms_chromatogram.get_peaks()[1], self.intensity))
        self.assertTrue(np.array_equal(pyopenms_chromatogram.get_peaks()[0], self.rt))

    def test_max(self):
        self.assertEqual(self.chromatogram.max(), (3,30.0))
        self.assertEqual(self.chromatogram.max((1.5, 2.5)), (2, 20.0))

    def test_filterChromatogram(self):
        filtered_chromatogram = self.chromatogram.filterChromatogram((1.5, 2.5))
        self.assertTrue(np.array_equal(filtered_chromatogram.rt, np.array([2.0])))
        self.assertTrue(np.array_equal(filtered_chromatogram.intensity, np.array([20.0])))

    def test_sum(self):
        self.assertEqual(self.chromatogram.sum(), 60.0)
        self.assertEqual(self.chromatogram.sum((1.5, 2.5)), 20.0)

    def test_median(self):
        self.assertEqual(self.chromatogram.median(), 20.0)
        self.assertEqual(self.chromatogram.median((1.5, 2.5)), 20.0)

if __name__ == '__main__':
    unittest.main()
