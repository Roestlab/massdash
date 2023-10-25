import unittest
from snapshottest import TestCase
import numpy as np
import pyopenms as po
from massseer.peak_picking import find_peak_boundaries, calculate_integrated_intensity, calculate_median_intensity, calculate_highest_intensity, get_peak_boundariers_for_single_chromatogram, merge_and_calculate_consensus_peak_boundaries, perform_chromatogram_peak_picking

class TestFindPeakBoundaries(TestCase):
    def test_find_peak_boundaries(self):
        # Create a PeakPickerMRM object and use it to pick the peaks in the chromatogram
        rt_peak_picker = po.PeakPickerMRM()
        peak_picker_params = rt_peak_picker.getParameters()
        peak_picker_params.setValue(b'gauss_width', 30.0)
        peak_picker_params.setValue(b'use_gauss', 'false')
        peak_picker_params.setValue(b'sgolay_frame_length',  11)
        peak_picker_params.setValue(b'sgolay_polynomial_order', 3)
        peak_picker_params.setValue(b'remove_overlapping_peaks', 'true')
        rt_peak_picker.setParameters(peak_picker_params)

        # Test case 1: Test with a single peak
        rt_arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                           11, 12, 13, 14, 15, 16, 17, 18, 19,
                           20, 21, 22, 23, 24, 25])
        rt_acc_im = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                              2, 3, 4, 5, 4, 3, 2, 1, 0,
                              0, 0, 0, 0, 0, 0])   
        output = find_peak_boundaries(rt_arr, rt_acc_im, rt_peak_picker)
        self.assertMatchSnapshot(output)

        # Test case 2: Test with multiple peaks
        rt_arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15, 16, 17, 18, 19,
                    20, 21, 22, 23, 24, 25, 26, 27, 28,
                    29, 30, 31, 32, 33, 34, 35, 36])
        rt_acc_im = np.array([0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                    2, 1, 0, 0, 0, 0, 0, 0, 0,
                    0, 1, 3, 9, 18, 25, 18, 9, 3,
                    1, 0, 0, 0, 0, 0, 0, 0])
        output = find_peak_boundaries(rt_arr, rt_acc_im, rt_peak_picker)
        self.assertMatchSnapshot(output)

        # Test case 3: Test with no peaks
        rt_arr = np.array([1, 2, 3, 4, 5])
        rt_acc_im = np.array([0, 0, 0, 0, 0])
        output = find_peak_boundaries(rt_arr, rt_acc_im, rt_peak_picker)
        self.assertMatchSnapshot(output)

class TestCalculateIntegratedIntensity(TestCase):
    def test_calculate_integrated_intensity_single_peak(self):
        chrom_data = [(range(1, 26), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0])]
        boundary = (10, 18)
        self.assertMatchSnapshot(calculate_integrated_intensity(chrom_data, boundary))

    def test_calculate_integrated_intensity_multiple_peaks(self):
        chrom_data = [(range(1, 37), [0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                                      2, 1, 0, 0, 0, 0, 0, 0, 0,
                                      0, 1, 3, 9, 18, 25, 18, 9, 3,
                                      1, 0, 0, 0, 0, 0, 0, 0])]
        boundary = (4, 12)
        self.assertMatchSnapshot(calculate_integrated_intensity(chrom_data, boundary))

class TestCalculateMedianIntensity(TestCase):
    def test_calculate_median_intensity_single_peak(self):
        chrom_data = [(range(1, 26), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0])]
        boundary = (10, 18)
        self.assertMatchSnapshot(calculate_median_intensity(chrom_data, boundary))

    def test_calculate_median_intensity_multiple_peaks(self):
        chrom_data = [(range(1, 37), [0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                                      2, 1, 0, 0, 0, 0, 0, 0, 0,
                                      0, 1, 3, 9, 18, 25, 18, 9, 3,
                                      1, 0, 0, 0, 0, 0, 0, 0])]
        boundary = (4, 12)
        self.assertMatchSnapshot(calculate_median_intensity(chrom_data, boundary))

class TestCalculateHighestIntensity(TestCase):
    def test_calculate_highest_intensity_single_peak(self):
        chrom_data = [(range(1, 26), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0])]
        boundary = (10, 18)
        self.assertMatchSnapshot(calculate_highest_intensity(chrom_data, boundary))

    def test_calculate_highest_intensity_multiple_peaks(self):
        chrom_data = [(range(1, 37), [0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                                      2, 1, 0, 0, 0, 0, 0, 0, 0,
                                      0, 1, 3, 9, 18, 25, 18, 9, 3,
                                      1, 0, 0, 0, 0, 0, 0, 0])]
        boundary = (4, 12)
        self.assertMatchSnapshot(calculate_highest_intensity(chrom_data, boundary))

class TestGetPeakBoundariesForSingleChromatogram(TestCase):
    def test_get_peak_boundaries_for_single_chromatogram_single_peak(self):
        chrom_data = [list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0]]
        rt_peak_picker = po.PeakPickerMRM()
        output = get_peak_boundariers_for_single_chromatogram(chrom_data, rt_peak_picker)
        self.assertMatchSnapshot(output)

    def test_get_peak_boundaries_for_single_chromatogram_multiple_peaks(self):
        chrom_data = [list(range(1, 37)), [0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                                      2, 1, 0, 0, 0, 0, 0, 0, 0,
                                      0, 1, 3, 9, 18, 25, 18, 9, 3,
                                      1, 0, 0, 0, 0, 0, 0, 0]]
        rt_peak_picker = po.PeakPickerMRM()
        output = get_peak_boundariers_for_single_chromatogram(chrom_data, rt_peak_picker)
        self.assertMatchSnapshot(output)

    def test_get_peak_boundaries_for_single_chromatogram_no_peaks(self):
        chrom_data = [list(range(1, 6)), [0, 0, 0, 0, 0]]
        rt_peak_picker = po.PeakPickerMRM()
        output = get_peak_boundariers_for_single_chromatogram(chrom_data, rt_peak_picker)
        self.assertMatchSnapshot(output)

class TestMergeAndCalculateConsensusPeakBoundaries(TestCase):
    def test_merge_and_calculate_consensus_peak_boundaries_single_chromatogram(self):
        chrom_data = [[list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0]]]
        rt_peak_picker = po.PeakPickerMRM()
        output = merge_and_calculate_consensus_peak_boundaries(chrom_data, rt_peak_picker)
        self.assertMatchSnapshot(output)

    def test_merge_and_calculate_consensus_peak_boundaries_multiple_chromatograms(self):
        chrom_data = [[list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0]],
                      [list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      1, 2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0]]]
        rt_peak_picker = po.PeakPickerMRM()
        output = merge_and_calculate_consensus_peak_boundaries(chrom_data, rt_peak_picker)
        self.assertMatchSnapshot(output)

    def test_merge_and_calculate_consensus_peak_boundaries_top_n_features(self):
        chrom_data = [[list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0]],
                      [list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      1, 2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0]]]
        rt_peak_picker = po.PeakPickerMRM()
        output = merge_and_calculate_consensus_peak_boundaries(chrom_data, rt_peak_picker, top_n_features=1)
        self.assertMatchSnapshot(output)

class TestPerformChromatogramPeakPicking(TestCase):
    def test_perform_chromatogram_peak_picking_single_peak(self):
        chrom_data_all = [list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                          2, 3, 4, 5, 4, 3, 2, 1, 0,
                                          0, 0, 0, 0, 0, 0]]
        do_smoothing = True
        sgolay_frame_length = 11
        sgolay_polynomial_order = 3
        merged_peak_picking = False
        output = perform_chromatogram_peak_picking(chrom_data_all, do_smoothing, sgolay_frame_length, sgolay_polynomial_order, merged_peak_picking)
        self.assertMatchSnapshot(output)

    def test_perform_chromatogram_peak_picking_multiple_peaks(self):
        chrom_data_all = [list(range(1, 37)), [0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                                          2, 1, 0, 0, 0, 0, 0, 0, 0,
                                          0, 1, 3, 9, 18, 25, 18, 9, 3,
                                          1, 0, 0, 0, 0, 0, 0, 0]]
        do_smoothing = True
        sgolay_frame_length = 11
        sgolay_polynomial_order = 3
        merged_peak_picking = False
        output = perform_chromatogram_peak_picking(chrom_data_all, do_smoothing, sgolay_frame_length, sgolay_polynomial_order, merged_peak_picking)
        self.assertMatchSnapshot(output)

    def test_perform_chromatogram_peak_picking_merged_peak_picking(self):
        chrom_data_all = [[list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                      2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0, 0]],
                      [list(range(1, 26)), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      1, 2, 3, 4, 5, 4, 3, 2, 1, 0,
                                      0, 0, 0, 0, 0]]]
        do_smoothing = True
        sgolay_frame_length = 11
        sgolay_polynomial_order = 3
        merged_peak_picking = True
        output = perform_chromatogram_peak_picking(chrom_data_all, do_smoothing, sgolay_frame_length, sgolay_polynomial_order, merged_peak_picking)
        self.assertMatchSnapshot(output)

if __name__ == '__main__':
    unittest.main()