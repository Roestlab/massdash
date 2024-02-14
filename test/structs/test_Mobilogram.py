import unittest
from massdash.structs import Mobilogram
import pandas as pd

class TestMobilogram(unittest.TestCase):

    def setUp(self):
        # Create a sample Mobilogram object for testing
        self.im = [0.98, 0.99, 1.0, 1.01, 1.02]
        self.intensity = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.label = "b4^1"
        self.mobilogram = Mobilogram(self.im, self.intensity, self.label)

    def test_toPandasDf(self):
        # Test the toPandasDf() method
        df = self.mobilogram.toPandasDf()
        expectedOutput = pd.DataFrame({'im': self.im, 'intensity': self.intensity, 'annotation': [self.label]*len(self.im)})
        self.assertIsInstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, expectedOutput)

    def test_adjust_length(self):
        # Test the adjust_length() method
        # other assumptions tested in data1D just have to check if returned mobilogram
        new_length = 10
        new_mobilogram = self.mobilogram.adjust_length(new_length)
        self.assertIsInstance(new_mobilogram, Mobilogram)

if __name__ == '__main__':
    unittest.main()
