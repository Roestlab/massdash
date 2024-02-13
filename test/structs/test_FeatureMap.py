"""
test/structs/test_FeatureMap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np

import unittest
from massdash.structs import FeatureMap, Chromatogram, Spectrum, Mobilogram


class TestFeatureMap(unittest.TestCase):
    def setUp(self):
        # Create a sample feature map DataFrame
        self.feature_df = pd.DataFrame({
            'mz': [100, 100.01, 100.02, 200.02,200.03] * 3, # note: not grouped by mz
            'rt': [10] * 5 + [20] * 5 + [30] * 5,
            'im': [1,2,2.5,3,3.5] * 3,
            'int': [50,10,15,20,20] * 3,
            'ms_level': [1, 2, 2, 2,2] * 3,
            'Annotation': ['prec', 'b2^2', 'b2^2', 'y3^3', 'y3^3'  ] * 3
        })

        self.empty_df = pd.DataFrame(columns=['mz', 'rt', 'im', 'int', 'ms_level', 'Annotation'])
        self.sequence = 'TEST'
        self.precursor_charge = 2
        self.config = None
        self.verbose = False

    def test_empty(self):
        ### test with filled feature map
        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        self.assertFalse(feature_map.empty())

        ## test with empty feature map
        feature_map = FeatureMap(self.empty_df, self.sequence, self.precursor_charge, self.config, self.verbose)

    def test_getitem(self):
        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        pd.testing.assert_series_equal(feature_map['mz'], self.feature_df['mz'])

    def test_setitem(self):
        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        toSet = pd.Series([400, 500, 600, 700, 800] * 3, name='mz')
        feature_map['mz'] = toSet
        pd.testing.assert_series_equal(feature_map['mz'], toSet)

    def test_get_precursor_chromatograms(self):
        feature_df = pd.DataFrame({
            'mz': [100, 100.01, 100.02,300], # note: not grouped by mz
            'rt': [10, 10, 20, 20],
            'im': [1,2,1,2],
            'int': [1,1,1,5],
            'ms_level': [1, 1, 1, 2],
            'Annotation': ['prec', 'prec', 'prec', 'b2^2' ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        chromatograms = feature_map.get_precursor_chromatograms()
        self.assertEqual(len(chromatograms), 1)
        chromatogram = chromatograms[0]
        self.assertEqual(chromatogram.label, 'prec')
        self.assertEqual(len(chromatogram.data), 2)
        np.testing.assert_almost_equal(chromatogram.data, [10,20])
        np.testing.assert_almost_equal(chromatogram.intensity, [2,1])
    
    def test_get_transition_chromatograms(self):
        feature_df = pd.DataFrame({
            'mz': [100, 100, 100.01, 200.02,200.03], # note: not grouped by mz
            'rt': [10, 10, 10, 10, 10],
            'im': [1,2,1,2,1],
            'int': [5,1,1,2,2],
            'ms_level': [1, 2, 2, 2, 2],
            'Annotation': ['prec', 'b2^2', 'b2^2', 'y3^3', 'y3^3'  ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        chromatograms = feature_map.get_transition_chromatograms()
        self.assertEqual(len(chromatograms), 2)
        self.assertIsInstance(chromatograms[0], Chromatogram)
        self.assertIsInstance(chromatograms[1], Chromatogram)

        self.assertEqual(chromatograms[0].label, 'b2^2')
        self.assertEqual(len(chromatograms[0].data), 1)
        self.assertEqual(chromatograms[0].data, [10])
        self.assertEqual(chromatograms[0].intensity, [2])

        self.assertEqual(chromatograms[1].label, 'y3^3')
        self.assertEqual(len(chromatograms[1].data), 1)
        self.assertEqual(chromatograms[1].data, [10])
        self.assertEqual(chromatograms[1].intensity, [4])
    
    '''
    def test_get_precursor_spectra(self):
        feature_df = pd.DataFrame({
            'mz': [100, 100.01, 100.02,300], # note: not grouped by mz
            'rt': [10, 10, 20, 20],
            'im': [1,1,1,1],
            'int': [1,1,1,5],
            'ms_level': [1, 1, 1, 2],
            'Annotation': ['prec', 'prec', 'prec', 'b2^2' ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        spectra = feature_map.get_precursor_spectra()
        self.assertEqual(len(spectra), 1)

        self.assertEqual(spectrum.label, 'prec')
        self.assertIsInstance(spectrum, Spectrum)

        self.assertEqual(len(spectrum.data), 3)
        self.assertEqual(spectrum.data, [100, 100.01, 100.02])
        self.assertEqual(spectrum.intensity, [1,1,1])

    
    def test_to_transition_spectra(self):
        feature_df = pd.DataFrame({
            'mz': [100, 100, 100.01, 200.02,200.03], # note: not grouped by mz
            'rt': [10, 10, 10, 10, 10],
            'im': [1,1,1,1,1],
            'int': [5,1,1,2,2],
            'ms_level': [1, 2, 2, 2, 2],
            'Annotation': ['prec', 'b2^2', 'b2^2', 'y3^3', 'y3^3'  ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        spectra = feature_map.get_transition_spectra()
        self.assertEqual(len(spectra), 2)
        self.assertIsInstance(spectra[0], Spectrum)
        self.assertIsInstance(spectra[1], Spectrum)

        self.assertEqual(spectra[0].label, 'b2^2')
        self.assertEqual(len(spectra[0].data), 2)
        self.assertEqual(spectra[0].data, [100, 100.01])
        self.assertEqual(spectra[0].intensity, [1,1])

        self.assertEqual(spectra[1].label, 'y3^3')
        self.assertEqual(len(spectra[1].data), 2)
        self.assertEqual(spectra[1].data, [200.02, 200.03])
        self.assertEqual(spectra[1].intensity, [2,2])
    '''
    
    def test_get_precursor_mobilogram(self):
        feature_df = pd.DataFrame({
            'mz': [100, 100.01, 100.02,300], # note: not grouped by mz
            'rt': [10, 20, 30, 40],
            'im': [1,1,2,2],
            'int': [1,1,1,5],
            'ms_level': [1, 1, 1, 2],
            'Annotation': ['prec', 'prec', 'prec', 'b2^2' ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        mobilograms = feature_map.get_precursor_mobilograms()
        self.assertEqual(len(mobilograms), 1)
        mobilogram = mobilograms[0]

        self.assertEqual(mobilogram.label, 'prec')
        self.assertIsInstance(mobilogram, Mobilogram)

        self.assertEqual(len(mobilogram.data), 2)
        np.testing.assert_almost_equal(mobilogram.data, [1,2])
        np.testing.assert_almost_equal(mobilogram.intensity, [2,1])

    def test_get_transition_mobilograms(self):
        feature_df = pd.DataFrame({
            'rt': [10, 10, 10, 20, 20],
            'im': [1,2,3,2,3],
            'int': [5,1,2,1,2],
            'ms_level': [1, 2, 2, 2, 2],
            'Annotation': ['prec', 'b2^2', 'y3^3', 'b2^2', 'y3^3' ]
        })
        feature_map = FeatureMap(feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        mobilograms = feature_map.get_transition_mobilograms()

        self.assertEqual(len(mobilograms), 2)
        self.assertIsInstance(mobilograms[0], Mobilogram)
        self.assertIsInstance(mobilograms[1], Mobilogram)

        self.assertEqual(mobilograms[0].label, 'b2^2')
        self.assertEqual(len(mobilograms[0].data), 2)
        np.testing.assert_almost_equal(mobilograms[0].data, [2,3])
        np.testing.assert_almost_equal(mobilograms[0].intensity, [2,0])

        self.assertEqual(mobilograms[1].label, 'y3^3')
        self.assertEqual(len(mobilograms[1].data), 2)
        np.testing.assert_almost_equal(mobilograms[1].data, [2,3])
        np.testing.assert_almost_equal(mobilograms[1].intensity, [0,4])


    def test_to_chromatograms(self):

        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        chromatograms = feature_map.to_chromatograms()
        
        ### Test Metadata matching
        chromatograms.sequence = self.sequence
        chromatograms.precursor_charge = self.precursor_charge

        # Test data matching
        precursor_chroms = chromatograms.precursorData
        transition_chroms = chromatograms.transitionData

        self.assertEqual(len(precursor_chroms), 1)
        self.assertEqual(len(transition_chroms), 2)

        self.assertIsInstance(precursor_chroms[0], Chromatogram)
        self.assertIsInstance(transition_chroms[0], Chromatogram)
        self.assertIsInstance(transition_chroms[1], Chromatogram)

        self.assertEqual(precursor_chroms[0].label, 'prec')
        self.assertEqual(len(precursor_chroms[0].data), 3)
        np.testing.assert_almost_equal(precursor_chroms[0].data, [10,20,30])
        np.testing.assert_almost_equal(precursor_chroms[0].intensity, [50,50,50])

        self.assertEqual(transition_chroms[0].label, 'b2^2')
        self.assertEqual(len(transition_chroms[0].data), 3)
        np.testing.assert_almost_equal(transition_chroms[0].data, [10,20,30])
        np.testing.assert_almost_equal(transition_chroms[0].intensity, [25,25,25])

        self.assertEqual(transition_chroms[1].label, 'y3^3')
        self.assertEqual(len(transition_chroms[1].data), 3)
        np.testing.assert_almost_equal(transition_chroms[1].data, [10,20,30])
        np.testing.assert_almost_equal(transition_chroms[1].intensity, [40,40,40])

    def test_to_mobilograms(self):

        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        mobilograms = feature_map.to_mobilograms()
        
        ## Test metadata equal
        mobilograms.sequence = self.sequence
        mobilograms.precursor_charge = self.precursor_charge

        ## Test data equal
        precursor_mobs = mobilograms.precursorData
        transition_mobs = mobilograms.transitionData

        self.assertEqual(len(precursor_mobs), 1)
        self.assertEqual(len(transition_mobs), 2)

        self.assertIsInstance(precursor_mobs[0], Mobilogram)
        self.assertIsInstance(transition_mobs[0], Mobilogram)
        self.assertIsInstance(transition_mobs[1], Mobilogram)

        self.assertEqual(precursor_mobs[0].label, 'prec')
        self.assertEqual(len(precursor_mobs[0].data), 1)
        np.testing.assert_almost_equal(precursor_mobs[0].data, [1])
        np.testing.assert_almost_equal(precursor_mobs[0].intensity, [150])

        self.assertEqual(transition_mobs[0].label, 'b2^2')
        self.assertEqual(len(transition_mobs[0].data), 4)
        np.testing.assert_almost_equal(transition_mobs[0].data, [2.0, 2.5, 3.0, 3.5])
        np.testing.assert_almost_equal(transition_mobs[0].intensity, [30,45, 0,0])

        self.assertEqual(transition_mobs[1].label, 'y3^3')
        self.assertEqual(len(transition_mobs[1].data), 4)
        np.testing.assert_almost_equal(transition_mobs[1].data, [2.0, 2.5, 3.0, 3.5])
        np.testing.assert_almost_equal(transition_mobs[1].intensity, [0, 0, 60, 60])

    '''
    def test_to_spectra(self):
        feature_map = FeatureMap(self.feature_df, self.sequence, self.precursor_charge, self.config, self.verbose)
        spectra = feature_map.to_spectra()
        self.assertEqual(len(spectra), 3)
        self.assertIsInstance(spectra[0], Spectrum)
        self.assertIsInstance(spectra[1], Spectrum)
        self.assertIsInstance(spectra[2], Spectrum)

        self.assertEqual(spectra[0].label, 'prec')
        self.assertEqual(len(spectra[0].data), len(self.feature_df['mz']))
        self.assertEqual(spectra[0].data, self.feature_df['mz'])
        self.assertEqual(spectra[0].intensity, self.feature_df['int'])
    '''

if __name__ == '__main__':
    unittest.main()
