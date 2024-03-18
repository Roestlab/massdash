"""
test/loaders/test_GenericSpectrumLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from massdash.loaders.GenericSpectrumLoader import GenericSpectrumLoader

class DummyGenericSpectrumLoader(GenericSpectrumLoader):
    pass

class TestGenericSpectrumLoader(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()