"""
test/peakPickers/test_MRMTransitionGroupPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from massdash.peakPickers.MRMTransitionGroupPicker import MRMTransitionGroupPicker
from massdash.structs.TransitionGroup import TransitionGroup
from massdash.structs.TransitionGroupFeature import TransitionGroupFeature
from massdash.structs.Chromatogram import Chromatogram
import pyopenms as po
from snapshottest import TestCase
import numpy as np

class TestMRMTransitionGroupPicker(TestCase):

    def setUp(self):
        rtdata_1 = np.array([1474.34, 1477.11, 1479.88, 1482.64, 1485.41, 1488.19, 1490.95, 1493.72, 1496.48, 1499.25, 1502.03, 1504.8, 1507.56, 1510.33, 1513.09, 1515.87, 1518.64, 1521.42])
        rtdata_2 = np.array([1473.55, 1476.31, 1479.08, 1481.84, 1484.61, 1487.39, 1490.15, 1492.92, 1495.69, 1498.45, 1501.23, 1504, 1506.76, 1509.53, 1512.29, 1515.07, 1517.84, 1520.62])

        intdata_1 = np.array([3.26958, 3.74189, 3.31075, 86.1901, 3.47528, 387.864, 13281, 6375.84, 39852.6, 2.66726, 612.747, 3.34313, 793.12, 3.29156, 4.00586, 4.1591, 3.23035, 3.90591])
        intdata_2 = np.array([3.44054, 2142.31, 3.58763, 3076.97, 6663.55, 45681, 157694, 122844, 86034.7, 85391.1, 15992.8, 2293.94, 6934.85, 2735.18, 459.413, 3.93863, 3.36564, 3.44005])
        ms1_intdata = np.array([900, 2600, 4100, 5400, 6500, 7400, 8100, 8600, 8900, 9000, 8900, 8600, 8100, 7400, 6500, 5400, 4100, 2600])

        chrom_1 = Chromatogram(rtdata_1, intdata_1)
        chrom_2 = Chromatogram(rtdata_2, intdata_2)
        chrom_ms1 = Chromatogram(rtdata_2 + 0.5, ms1_intdata)

        self.tg_1 = TransitionGroup([chrom_ms1], [chrom_1, chrom_2])

        # Initialize the second transition group (based on OpenMS MRMTransitioonGroupPicker_test)
        rtdata = np.arange(0, 30)

        intdata_1 = np.array([3,3,3,3,3,3,3,3,4,6,8,12,14,15,16,15,14,12,8,6,4,3,3,3,3,3,3,3,3,3])
        intdata_2 = np.array([3,3,4,6,8,10,11,11,10,8,6,4,4,6,8,10,11,11,10,8,6,4,3,3,3,3,3,3,3,3])
        intdata_3 = np.full(30, 3.0)

        chrom_1 = Chromatogram(rtdata, intdata_1)
        chrom_2 = Chromatogram(rtdata, intdata_2)
        chrom_3 = Chromatogram(rtdata, intdata_3)

        self.tg_2 = TransitionGroup([], [chrom_1, chrom_2, chrom_3])

        rt_arr_short = np.arange(1, 6)
        rt_arr = np.arange(1, 26)
        rt_arr_long = np.arange(1, 37)

        ### Create different intensity arrays for testing ###
        empty_intens = np.zeros(5)
        intens_single_peak = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                              2, 3, 4, 5, 4, 3, 2, 1, 0,
                              0, 0, 0, 0, 0, 0])   
        intens_multiple_peaks = np.array([0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                    2, 1, 0, 0, 0, 0, 0, 0, 0,
                    0, 1, 3, 9, 18, 25, 18, 9, 3,
                    1, 0, 0, 0, 0, 0, 0, 0])
        

        ### Create empty transition group for testing ###
        chrom_empty = Chromatogram(rt_arr_short, empty_intens)
        self.transition_group_empty = TransitionGroup([chrom_empty],[])


         
        ### Create Chromatograms for testing ####
        self.tg_3 = TransitionGroup([chrom_1], [chrom_3])# only peak in precursor signal
        self.chrom_single_peak = Chromatogram(rt_arr, intens_single_peak)
        self.chrom_multiple_peaks = Chromatogram(rt_arr_long, intens_multiple_peaks)



    def test_setGeneralParameters(self):
        # Test setting of parameters
        picker = MRMTransitionGroupPicker("original")
        picker.setGeneralParameters(stop_after_feature=5, signal_to_noise=1000.0)
        val = picker.params.getValue(b'stop_after_feature')
        self.assertEqual(val, 5)
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:signal_to_noise'), 1000.0)

        # Test setting of invalid parameterata/xics/test_chrom_1.sqMass', '../test_data/xics/test_chrom_2.sqMass'], rsltsFile="../test_data/osw/test_data.osw")
        with self.assertRaises(ValueError):
            picker.setGeneralParameters(invalid_param=5)

    def test_setSmoother(self):
        # Test setting of smoother
        picker = MRMTransitionGroupPicker("original")
        
        # Test setting of original smoother
        picker.setSmoother("original")
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:method'),  'legacy')

        # Test setting of gaussian smoother
        picker.setSmoother("gauss", gauss_width=10.0)
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:method'),  'corrected')
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:use_gauss'),  'true')
        self.assertEqual((picker.params.getValue(b'PeakPickerMRM:gauss_width')), 10.0)

        picker.setSmoother("sgolay")
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:method'), 'corrected')
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:use_gauss'), 'false')
        self.assertEqual(picker.params.getValue(b'PeakPickerMRM:sgolay_frame_length'), 11)

        # Test setting of invalid smoother
        with self.assertRaises(ValueError):
            picker.setSmoother("invalid_smoother")

    def test_pick_empty(self):
        ### Test empty transition group ###
        picker = MRMTransitionGroupPicker("original")
        tg_feature = picker.pick(self.transition_group_empty)
        self.assertEqual(len(tg_feature), 0)

    def test_pick_1(self):

        ### Test example #1, a bit of a blackbox test ##
        picker = MRMTransitionGroupPicker("original")
        tg_feature = picker.pick(self.tg_1)

        print(tg_feature)
        self.assertEqual(len(tg_feature), 1)
        self.assertAlmostEqual(tg_feature[0].consensusApex, 1498.86, places=3)
        self.assertAlmostEqual(tg_feature[0].areaIntensity, 232025.296875, places=3)
        self.assertAlmostEqual(tg_feature[0].leftBoundary, 1493.72, places=3)
        self.assertAlmostEqual(tg_feature[0].rightBoundary, 1504.0, places=3)

    def test_pick_2(self):
        ### Test example #2 ##
        ### Test with background subtraction ###
        picker = MRMTransitionGroupPicker("original")
        picker.setGeneralParameters(background_subtraction="original")
        tg_feature = picker.pick(self.tg_1)
        print(tg_feature)
        self.assertEqual(len(tg_feature), 1)
        self.assertAlmostEqual(tg_feature[0].consensusApex, 1498.86, places=3)
        self.assertAlmostEqual(tg_feature[0].areaIntensity, 41390.84, places=3)
        self.assertAlmostEqual(tg_feature[0].leftBoundary, 1493.72, places=3)
        self.assertAlmostEqual(tg_feature[0].rightBoundary, 1504.0, places=3)

    def test_pick_3(self):
        ### Transition group #2 direct from C++ implementation ##
        picker = MRMTransitionGroupPicker("gauss", gauss_width=10.0)
        picker.setGeneralParameters(signal_to_noise=1.0, resample_boundary=1.0, recalculate_peaks_max_z=1.0, recalculate_peaks="false")
        tg_feature = picker.pick(self.tg_2)
        print(tg_feature)
        self.assertEqual(len(tg_feature), 1)
        self.assertAlmostEqual(tg_feature[0].consensusApex, 14, places=5)
        self.assertAlmostEqual(tg_feature[0].areaIntensity, 302, places=5) 
        self.assertAlmostEqual(tg_feature[0].leftBoundary, 7, places=5)
        self.assertAlmostEqual(tg_feature[0].rightBoundary, 21, places=5)

    def test_pick_4(self):
        ### Transition group #2 black box test ##
        picker = MRMTransitionGroupPicker("sgolay")
        tg_feature = picker.pick(self.tg_2)
        print(tg_feature)
        self.assertEqual(len(tg_feature), 1)
        self.assertAlmostEqual(tg_feature[0].consensusApex, 14, places=5)
        self.assertAlmostEqual(tg_feature[0].areaIntensity, 353, places=5) ### not sure if this is correct
        self.assertAlmostEqual(tg_feature[0].leftBoundary, 5, places=5)
        self.assertAlmostEqual(tg_feature[0].rightBoundary, 23, places=5)

    def test_pick_4(self):
        ### Transition group #3 for testing with precursors##
        picker = MRMTransitionGroupPicker("original")
        picker.setGeneralParameters(use_precursors="true")
        tg_feature = picker.pick(self.tg_3)
        print(tg_feature)
        self.assertEqual(len(tg_feature), 1)
        self.assertAlmostEqual(tg_feature[0].consensusApex, 14, places=5)
        self.assertAlmostEqual(tg_feature[0].areaIntensity, 45, places=5)
        self.assertAlmostEqual(tg_feature[0].leftBoundary, 7, places=5)
        self.assertAlmostEqual(tg_feature[0].rightBoundary, 21, places=5)




    def test_convertPyopenMSFeaturesToPeakFeatures(self):
        picker = MRMTransitionGroupPicker('original')
        # Create a dummy pyopenms feature
        pyopenmsFeature = po.Feature()
        pyopenmsFeature.setMetaValue(b'leftWidth', 1.0)
        pyopenmsFeature.setMetaValue(b'rightWidth', 2.0)
        pyopenmsFeature.setIntensity(3.0)
        pyopenmsFeature.setRT(4.0)

        # Call the _convertPyopenMSFeaturesToPeakFeatures method and check that it returns a list of PeakFeature objects
        peakFeatures = picker._convertPyopenMSFeaturesToTransitionGroupFeatures([pyopenmsFeature])
        self.assertIsInstance(peakFeatures, list)
        self.assertEqual(len(peakFeatures), 1)
        feature = peakFeatures[0]
        self.assertIsInstance(feature, TransitionGroupFeature)
        self.assertEqual(feature.leftBoundary, 1.0)
        self.assertEqual(feature.rightBoundary, 2.0)
        self.assertEqual(feature.areaIntensity, 3.0)
        self.assertEqual(feature.consensusApex, 4.0)

if __name__ == '__main__':
    unittest.main()
