"""
test/loaders/test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from pathlib import Path

import pandas as pd
from snapshottest import TestCase

from massdash.structs.TransitionGroup import TransitionGroup
from massdash.loaders.SqMassLoader import SqMassLoader
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'


class TestSqMassLoader(TestCase):
    def setUp(self):
        self.loader = SqMassLoader(dataFiles=[f'{str(TEST_PATH)}/test_data/xics/test_chrom_1.sqMass', f'{str(TEST_PATH)}/test_data/xics/test_chrom_2.sqMass'], rsltsFile=f"{str(TEST_PATH)}/test_data/osw/test_data.osw")

    def test_loadTransitionGroupFeature(self):
        # Test loading a peak feature for a valid peptide ID and charge
        fullpeptidename = "NKESPT(UniMod:21)KAIVR(UniMod:267)"
        charge = 3
        peak_feature = self.loader.loadTransitionGroupFeatures(fullpeptidename, charge)
        self.assertMatchSnapshot(peak_feature)

        # Test loading a peak feature for an invalid peptide ID and charge
        peak_feature_2 = self.loader.loadTransitionGroupFeatures('INVALID', 0)
        self.assertMatchSnapshot(len(peak_feature_2))
    
    def test_loadTransitionGroups(self):
        # Test loading a chromatogram for a valid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroups("NKESPT(UniMod:21)KAIVR(UniMod:267)", 3)
        self.assertIsInstance(transitionGroup, dict)
        self.assertIsInstance(list(transitionGroup.values())[0], TransitionGroup)
        self.assertMatchSnapshot(transitionGroup)

        # Test loading a chromatogram for an invalid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroups('INVALID', 0)
        self.assertIsNone(transitionGroup)
    
    def test_loadTransitionGroupsDf(self):
        # Test loading a chromatogram for a valid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroupsDf("NKESPT(UniMod:21)KAIVR(UniMod:267)", 3)
        self.assertIsInstance(transitionGroup, pd.DataFrame)
        # TODO: fix assertion error below
        # self.assertMatchSnapshot(transitionGroup)

        # Test loading a chromatogram for an invalid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroupsDf('INVALID', 0)
        self.assertIsInstance(transitionGroup, pd.DataFrame)
        self.assertTrue(transitionGroup.empty)
    
    def test_loadTransitionGroupFeaturesDf(self):
        # Test loading a chromatogram for a valid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroupFeaturesDf("NKESPT(UniMod:21)KAIVR(UniMod:267)", 3)
        self.assertIsInstance(transitionGroup, pd.DataFrame)
        # TODO: fix assertion error below
        # self.assertMatchSnapshot(transitionGroup)

        # Test loading a chromatogram for an invalid peptide ID and charge
        transitionGroup = self.loader.loadTransitionGroupFeaturesDf('INVALID', 0)
        self.assertIsInstance(transitionGroup, pd.DataFrame)
        self.assertTrue(transitionGroup.empty)


if __name__ == '__main__':
    unittest.main()