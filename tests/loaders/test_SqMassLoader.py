from snapshottest import TestCase
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.loaders.SqMassLoader import SqMassLoader
import unittest

class TestSqMassLoader(TestCase):
    def setUp(self):
        self.loader = SqMassLoader(transitionFiles=['../test_data/xics/test_chrom_1.sqMass', '../test_data/xics/test_chrom_2.sqMass'], rsltsFile="../test_data/osw/test_data.osw")

    def test_loadTransitionGroupFeature(self):
        # Test loading a peak feature for a valid peptide ID and charge
        fullpeptidename = "NKESPT(UniMod:21)KAIVR(UniMod:267)"
        charge = 3
        peak_feature = self.loader.loadTransitionGroupFeature(fullpeptidename, charge)
        self.assertMatchSnapshot(peak_feature)

        # Test loading a peak feature for an invalid peptide ID and charge
        peak_feature = self.loader.loadTransitionGroupFeature('INVALID', 0)
        self.assertMatchSnapshot(len(peak_feature))
    
    def test_loadTransitionGroups(self):
        # Test loading a chromatogram for a valid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroups("NKESPT(UniMod:21)KAIVR(UniMod:267)", 3)
        self.assertIsInstance(transitionGroup, dict)
        self.assertIsInstance(list(transitionGroup.values())[0], TransitionGroup)
        self.assertMatchSnapshot(transitionGroup)

        # Test loading a chromatogram for an invalid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroups('INVALID', 0)
        self.assertIsNone(transitionGroup)

if __name__ == '__main__':
    unittest.main()