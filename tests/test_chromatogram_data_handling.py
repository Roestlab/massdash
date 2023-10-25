import unittest
from snapshottest import TestCase
import numpy as np
from massseer.chromatogram_data_handling import get_chrom_data_limits, pad_data, get_max_rt_array_length, get_chrom_data_global, normalize, average_chromatograms, median_chromatograms, percentile_average_chromatograms, compute_threshold, compute_consensus_chromatogram

class TestChromatogramDataHandling(TestCase):
    def test_get_chrom_data_limits(self):
        # Test with dictionary input
        chrom_data_dict = {
            'file1': {'rt_start': 1.0, 'rt_end': 10.0, 'max_int': 100.0},
            'file2': {'rt_start': 2.0, 'rt_end': 20.0, 'max_int': 200.0},
            'file3': {'rt_start': 3.0, 'rt_end': 30.0, 'max_int': 300.0}
        }
        x_range, y_range = get_chrom_data_limits(chrom_data_dict)
        self.assertMatchSnapshot(x_range)
        self.assertMatchSnapshot(y_range)

        # Test with list input
        chrom_data_list = [
            [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
            [np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],
            [np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])]
        ]
        x_range, y_range = get_chrom_data_limits(chrom_data_list, data_type='list')
        self.assertMatchSnapshot(x_range)
        self.assertMatchSnapshot(y_range)

        # Test with set_x_range=False
        x_range, y_range = get_chrom_data_limits(chrom_data_dict, set_x_range=False)
        assert x_range is None
        self.assertMatchSnapshot(y_range)

        # Test with set_y_range=False
        x_range, y_range = get_chrom_data_limits(chrom_data_dict, set_y_range=False)
        self.assertMatchSnapshot(x_range)
        assert y_range is None

    def test_pad_data(self):
        # Test with data length less than max_length
        data = [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]
        max_length = 5
        padded_data = pad_data(data, max_length)
        self.assertMatchSnapshot(padded_data)

        # Test with data length equal to max_length
        data = [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]
        max_length = 3
        padded_data = pad_data(data, max_length)
        self.assertMatchSnapshot(padded_data)

        # Test with data length greater than max_length
        data = [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]
        max_length = 2
        padded_data = pad_data(data, max_length)
        self.assertMatchSnapshot(padded_data,)

    def test_get_max_rt_array_length(self):
        # Test with dictionary input
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],),
                              ([np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])],)]},
            'file2': {'ms1': [np.array([1.0, 2.0]), np.array([10.0, 20.0])],
                      'ms2': [([np.array([4.0, 5.0]), np.array([40.0, 50.0])],)]},
            'file3': {'ms1': [np.array([1.0]), np.array([10.0])],
                      'ms2': [([np.array([4.0]), np.array([40.0])],)]}
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input and include_ms1=False
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict, include_ms1=False)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input and include_ms2=False
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict, include_ms2=False)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input and include_ms1=False and include_ms2=False
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict, include_ms1=False, include_ms2=False)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with empty dictionary input
        chrom_data_dict = {}
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with no ms1 or ms2 data
        chrom_data_dict = {
            'file1': {},
            'file2': {},
            'file3': {}
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with only ms1 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]},
            'file2': {'ms1': [np.array([1.0, 2.0]), np.array([10.0, 20.0])]},
            'file3': {'ms1': [np.array([1.0]), np.array([10.0])]}
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with only ms2 data
        chrom_data_dict = {
            'file1': {'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],),
                              ([np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])],)]},
            'file2': {'ms2': [([np.array([4.0, 5.0]), np.array([40.0, 50.0])],)]},
            'file3': {'ms2': [([np.array([4.0]), np.array([40.0])],)]}
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with only one ms2 data
        chrom_data_dict = {
            'file1': {'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],)]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with only one ms1 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with one ms1 data and one ms2 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],)]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with one ms1 data and two ms2 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],),
                              ([np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])],)]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with two ms1 data and one ms2 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]},
            'file2': {'ms1': [np.array([1.0, 2.0]), np.array([10.0, 20.0])]},
            'file3': {'ms1': [np.array([1.0]), np.array([10.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],)]}
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with two ms1 data and two ms2 data
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]},
            'file2': {'ms1': [np.array([1.0, 2.0]), np.array([10.0, 20.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],)]},
            'file3': {'ms1': [np.array([1.0]), np.array([10.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],),
                              ([np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])],)]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

        # Test with dictionary input with two ms1 data and two ms2 data with different lengths
        chrom_data_dict = {
            'file1': {'ms1': [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])]},
            'file2': {'ms1': [np.array([1.0, 2.0]), np.array([10.0, 20.0])],
                      'ms2': [([np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],)]},
            'file3': {'ms1': [np.array([1.0]), np.array([10.0])],
                      'ms2': [([np.array([4.0, 5.0]), np.array([40.0, 50.0])],),
                              ([np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])],)]},
        }
        max_rt_array_length = get_max_rt_array_length(chrom_data_dict)
        self.assertMatchSnapshot(max_rt_array_length)

    def test_get_chrom_data_global(self):
        # Test with include_ms1=True and include_ms2=True
        # Set np seed to regenerate the same np.random.rand() values
        np.random.seed(0)
        chrom_data = {
            'file1': {'ms1': [[list(np.arange(30)), list(np.random.rand(30))]],
                      'ms2': [[[list(np.arange(30)), list(np.random.rand(30))]]]},
            'file2': {'ms1': [[list(np.arange(30)), list(np.random.rand(30))]],
                      'ms2': [[[list(np.arange(30)), list(np.random.rand(30))]]]},
            'file3': {'ms1': [[list(np.arange(30)), list(np.random.rand(30))]],
                      'ms2': [[[list(np.arange(30)), list(np.random.rand(30))]]]}
        }
        chrom_data_global = get_chrom_data_global(chrom_data, include_ms1=True, include_ms2=True)
        self.assertMatchSnapshot(chrom_data_global)

        # Test with include_ms1=False and include_ms2=True
        chrom_data_global = get_chrom_data_global(chrom_data, include_ms1=False, include_ms2=True)
        self.assertMatchSnapshot(chrom_data_global)

        # Test with include_ms1=True and include_ms2=False
        chrom_data_global = get_chrom_data_global(chrom_data, include_ms1=True, include_ms2=False)
        self.assertMatchSnapshot(chrom_data_global)

        # Test with include_ms1=False and include_ms2=False
        chrom_data_global = get_chrom_data_global(chrom_data, include_ms1=False, include_ms2=False)
        self.assertMatchSnapshot(chrom_data_global)

        # Test with empty dictionary input
        chrom_data = {}
        chrom_data_global = get_chrom_data_global(chrom_data, include_ms1=True, include_ms2=True)
        self.assertMatchSnapshot(chrom_data_global)
    
    def test_normalize(self):
        # Test with all zeros
        intensity = [0, 0, 0, 0]
        normalized_intensity = normalize(intensity)
        self.assertMatchSnapshot(normalized_intensity)

        # Test with positive values
        intensity = [100, 50, 150, 75]
        normalized_intensity = normalize(intensity)
        self.assertMatchSnapshot(normalized_intensity)

        # Test with negative values
        intensity = [-100, -50, -150, -75]
        normalized_intensity = normalize(intensity)
        self.assertMatchSnapshot(normalized_intensity)

        # Test with mixed positive and negative values
        intensity = [-100, 50, -150, 75]
        normalized_intensity = normalize(intensity)
        self.assertMatchSnapshot(normalized_intensity)

    def test_average_chromatograms(self):
        # Test with scale_intensity=False
        chrom_data = [
            [[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]],
            [[1.0, 2.0, 3.0], [20.0, 30.0, 40.0]],
            [[1.0, 2.0, 3.0], [30.0, 40.0, 50.0]]
        ]
        result = average_chromatograms(chrom_data, scale_intensity=False)
        self.assertMatchSnapshot(result)

        # Test with scale_intensity=True
        chrom_data = [
            [[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]],
            [[1.0, 2.0, 3.0], [20.0, 30.0, 40.0]],
            [[1.0, 2.0, 3.0], [30.0, 40.0, 50.0]]
        ]
        result = average_chromatograms(chrom_data, scale_intensity=True)
        self.assertMatchSnapshot(result)

        # Test with varying sublist lengths
        chrom_data = [
            [[1.0, 2.0, 3.0], [10.0, 20.0]],
            [[1.0, 2.0, 3.0], [20.0, 30.0, 40.0]],
            [[1.0, 2.0, 3.0], [30.0, 40.0, 50.0, 60.0]]
        ]
        result = average_chromatograms(chrom_data, scale_intensity=False)
        self.assertMatchSnapshot(result)

    def test_median_chromatograms(self):
        # Test with one chromatogram
        chrom_data = [[[1, 2, 3], [10, 20, 30]]]
        result = median_chromatograms(chrom_data)
        self.assertMatchSnapshot(result)

        # Test with two chromatograms of equal length
        chrom_data = [[[1, 2, 3], [10, 20, 30]], [[1, 2, 3], [20, 30, 40]]]
        result = median_chromatograms(chrom_data)
        self.assertMatchSnapshot(result)

        # Test with two chromatograms of different length
        chrom_data = [[[1, 2, 3], [10, 20, 30]], [[1, 2], [20, 30]]]
        result = median_chromatograms(chrom_data)
        self.assertMatchSnapshot(result)

        # Test with min-max scaling
        chrom_data = [[[1, 2, 3], [10, 20, 30]], [[1, 2, 3], [20, 30, 40]]]
        result = median_chromatograms(chrom_data, scale_intensity=True)
        self.assertMatchSnapshot(result)

    def test_percentile_average_chromatograms(self):
        # Test with default arguments
        chrom_data = [
            [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
            [np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],
            [np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])]
        ]
        result = percentile_average_chromatograms(chrom_data)
        self.assertMatchSnapshot(result)

        # Test with custom arguments
        chrom_data = [
            [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
            [np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],
            [np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])]
        ]
        percentile_start = 20
        percentile_end = 80
        threshold = 20
        scale_intensity = True
        result = percentile_average_chromatograms(chrom_data, percentile_start, percentile_end, threshold, scale_intensity)
        self.assertMatchSnapshot(result)

    def test_compute_threshold(self):
        # Test with single chromatogram data
        chrom_data = [(np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0]))]
        threshold = compute_threshold(chrom_data)
        self.assertMatchSnapshot(threshold)

        # Test with multiple chromatogram data
        chrom_data = [
            (np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])),
            (np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])),
            (np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0]))
        ]
        threshold = compute_threshold(chrom_data)
        self.assertMatchSnapshot(threshold)

        # Test with percentile_threshold=50
        chrom_data = [
            (np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])),
            (np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])),
            (np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0]))
        ]
        threshold = compute_threshold(chrom_data, percentile_threshold=50)
        self.assertMatchSnapshot(threshold)

        # Test with percentile_threshold=90
        chrom_data = [
            (np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])),
            (np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])),
            (np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0]))
        ]
        threshold = compute_threshold(chrom_data, percentile_threshold=90)
        self.assertMatchSnapshot(threshold)

    def test_compute_consensus_chromatogram(self):
        # Test with 'averaged' mode
        chrom_data_all = [
            [np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])],
            [np.array([4.0, 5.0, 6.0]), np.array([40.0, 50.0, 60.0])],
            [np.array([7.0, 8.0, 9.0]), np.array([70.0, 80.0, 90.0])]
        ]
        consensus_chrom_mode = 'averaged'
        scale_intensity = False
        percentile_start = 0
        percentile_end = 0
        threshold = 0
        auto_threshold = False
        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        self.assertMatchSnapshot(averaged_chrom_data)

        # Test with 'median' mode
        consensus_chrom_mode = 'median'
        median_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        self.assertMatchSnapshot(median_chrom_data)

        # Test with 'percentile_average' mode and auto_threshold=True
        consensus_chrom_mode = 'percentile_average'
        percentile_start = 10
        percentile_end = 90
        auto_threshold = True
        percentile_average_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        self.assertMatchSnapshot(percentile_average_chrom_data)

        # Test with 'percentile_average' mode and auto_threshold=False
        auto_threshold = False
        threshold = 50
        percentile_average_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        self.assertMatchSnapshot(percentile_average_chrom_data)

if __name__ == '__main__':
    unittest.main()