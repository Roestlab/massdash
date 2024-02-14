
import unittest
from massdash.structs import Spectrum
import pandas as pd

class TestSpectrum(unittest.TestCase):

    def setUp(self):
        # Create a sample Mobilogram object for testing
        self.mz = [100.0, 100.1, 100.2, 100.3, 100.4]
        self.intensity = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.label = "b4^1"
        self.spectrum = Spectrum(self.mz, self.intensity, self.label)

    def test_toPandasDf(self):
        # Test the toPandasDf() method
        df = self.spectrum.toPandasDf()
        expectedOutput = pd.DataFrame({'mz': self.mz, 'intensity': self.intensity, 'annotation': [self.label]*len(self.mz)})
        self.assertIsInstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, expectedOutput)

    def test_adjust_length(self):
        # Test the adjust_length() method
        # other assumptions tested in data1D just have to check if returned mobilogram
        new_length = 10
        new_spectrum = self.spectrum.adjust_length(new_length)
        self.assertIsInstance(new_spectrum, Spectrum)

if __name__ == '__main__':
    unittest.main()
