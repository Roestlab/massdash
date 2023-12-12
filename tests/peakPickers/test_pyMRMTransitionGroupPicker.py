
import unittest
from snapshottest import TestCase
import numpy as np

# Internal modules
from massseer.peakPickers import pyMRMTransitionGroupPicker
from massseer.structs import Chromatogram, TransitionGroup

class TestFindPeakBoundaries(TestCase):
    def setUp(self):
        self.pyPeakPicker = pyMRMTransitionGroupPicker(sgolay_frame_length=11, sgolay_polynomial_order=3)

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
        
        ### Create Chromatograms for testing ####
        self.chrom_empty = Chromatogram(rt_arr_short, empty_intens)
        self.chrom_single_peak = Chromatogram(rt_arr, intens_single_peak)
        self.chrom_multiple_peaks = Chromatogram(rt_arr_long, intens_multiple_peaks)

    def test_find_peak_boundaries(self):
        # Test case 1: Test with a single peak
        output = self.pyPeakPicker.find_peak_boundaries(self.chrom_single_peak) 
        self.assertMatchSnapshot(output)

        # Test case 2: Test with multiple peaks
        output2 = self.pyPeakPicker.find_peak_boundaries(self.chrom_multiple_peaks)
        self.assertMatchSnapshot(output2)

        # Test case 3: Test with no peaks
        output3 = self.pyPeakPicker.find_peak_boundaries(self.chrom_empty)
        self.assertMatchSnapshot(output3)

    ### Test pick ###
    def test_perform_chromatogram_peak_picking_single_peak(self):
        picker = pyMRMTransitionGroupPicker(sgolay_frame_length=11, sgolay_polynomial_order=3)
        output = picker.pick(TransitionGroup([self.chrom_single_peak], [], [], [], [], []))
        self.assertMatchSnapshot(output)

    def test_perform_chromatogram_peak_picking_multiple_peaks(self):
        picker = pyMRMTransitionGroupPicker(sgolay_frame_length=11, sgolay_polynomial_order=3)
        output = picker.pick(TransitionGroup([self.chrom_multiple_peaks], [], [], [], [], []))
        self.assertMatchSnapshot(output)

    def test_perform_chromatogram_peak_picking_merged_peak_picking(self):
        picker = pyMRMTransitionGroupPicker(sgolay_frame_length=11, sgolay_polynomial_order=3, level='ms1ms2')
        output = picker.pick(TransitionGroup([self.chrom_single_peak, self.chrom_single_peak], [], [], [], [], []))
        self.assertMatchSnapshot(output)

    ### Test get Level ###
    def test_resolve_level(self):
        tg = TransitionGroup([self.chrom_single_peak, self.chrom_empty], [self.chrom_multiple_peaks], [], [], [], [])

        picker = pyMRMTransitionGroupPicker(level='ms1ms2')
        output = picker._resolveLevel(tg)
        self.assertMatchSnapshot(output)

        picker = pyMRMTransitionGroupPicker(level='ms2')
        output = picker._resolveLevel(tg)
        self.assertMatchSnapshot(output)

        picker = pyMRMTransitionGroupPicker(level='ms1')
        output = picker._resolveLevel(tg)
        self.assertMatchSnapshot(output)


if __name__ == '__main__':
    unittest.main()
