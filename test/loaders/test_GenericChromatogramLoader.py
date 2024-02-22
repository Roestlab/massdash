import unittest
from massdash.loaders.GenericChromatogramLoader import GenericChromatogramLoader



class DummyGenericChromatogramLoader(GenericChromatogramLoader):
    pass

class TestGenericChromatogramLoader(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()