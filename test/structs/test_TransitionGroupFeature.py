"""
test/structs/test_TransitionGroupFeature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from massdash.structs.TransitionGroupFeature import TransitionGroupFeature

class TestTransitionGroupFeature(unittest.TestCase):

    def setUp(self):
        self.leftBoundary = 0.0
        self.rightBoundary = 1.0
        self.areaIntensity = 100.0
        self.qvalue = 0.05
        self.consensusApex = 0.5
        self.consensusApexIntensity = 50.0
        self.transitionGroupFeature = TransitionGroupFeature(self.leftBoundary, self.rightBoundary, self.areaIntensity, self.qvalue, self.consensusApex, self.consensusApexIntensity)

    def test_getBoundaries(self):
        self.assertEqual(self.transitionGroupFeature.getBoundaries(), (self.leftBoundary, self.rightBoundary))

    def test_toPanadsDf(self):
        df = TransitionGroupFeature.toPanadsDf([self.transitionGroupFeature])
        self.assertEqual(df.iloc[0]['leftBoundary'], self.leftBoundary)
        self.assertEqual(df.iloc[0]['rightBoundary'], self.rightBoundary)
        self.assertEqual(df.iloc[0]['areaIntensity'], self.areaIntensity)
        self.assertEqual(df.iloc[0]['qvalue'], self.qvalue)
        self.assertEqual(df.iloc[0]['consensusApex'], self.consensusApex)
        self.assertEqual(df.iloc[0]['consensusApexIntensity'], self.consensusApexIntensity)

if __name__ == '__main__':
    unittest.main()
