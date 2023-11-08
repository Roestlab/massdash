
import numpy as np
from massseer.structs.Chromatogram import Chromatogram
import pyopenms as po
from snapshottest import TestCase

def test_chromatogram(TestCase):
    
    def setUp(self):
        # Create a test chromatogram
        self.chromatogram = Chromatogram(np.array([1, 2, 3, 4, 5]), np.array([10, 20, 30, 40, 50]), "test")


    def test_to_pyopenms(self):
        # Test to_pyopenms method
        pyopenms_chromatogram = self.chromatogram.to_pyopenms()
        self.assertIsInstance(pyopenms_chromatogram, po.Chromatogram)
        self.assertMatchSnapShot(pyopenms_chromatogram) 

    def max(self):
        # Test max method
        assert self.chromatogram.max() == 50
        assert self.chromatogram.max((2, 4)) == 40

    # Test max method
    assert chromatogram.max() == 50
    assert chromatogram.max((2, 4)) == 40

    # Test filterChromatogram method
    filtered_chromatogram = chromatogram.filterChromatogram((2, 4))
    assert np.array_equal(filtered_chromatogram.rt, np.array([3, 4]))
    assert np.array_equal(filtered_chromatogram.intensity, np.array([30, 40]))

    # Test sum method
    assert chromatogram.sum() == 150
    assert chromatogram.sum((2, 4)) == 70

    # Test median method
    assert chromatogram.median() == 30
    assert chromatogram.median((2, 4)) == 35

    # Test snapshot of the chromatogram object
    snapshot.assert_match(chromatogram.__dict__)
