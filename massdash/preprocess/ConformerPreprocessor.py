"""
massdash/preprocess/ConformerPreprocessor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np
from typing import List, Literal

# Preprocess
from .GenericPreprocessor import GenericPreprocessor 
# Structs
from ..structs.TransitionGroup import TransitionGroup
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
# Utils
from ..util import check_package

torch, TORCH_AVAILABLE = check_package("torch")
binary_recall_at_fixed_precision, TORCHMETRICS_AVAILABLE = check_package("torchmetrics", "functional.classification.binary_recall_at_fixed_precision")

class ConformerPreprocessor(GenericPreprocessor):
    """
    A class that represents a preprocessor for Conformer models.

    Args:
        transition_group (TransitionGroup): The transition group containing the data.

    Attributes:
        transition_group (TransitionGroup): The transition group containing the data.

    Methods:
        min_max_scale(data, min=None, max=None): Performs min-max scaling on the data.
        find_thresholds(preds, target, min_precisions): Finds thresholds based on precision and recall.
        sigmoid(x): Applies the sigmoid function to the input.
        preprocess(): Preprocesses the data for require input structure for conformer model.
        find_top_peaks(preds, seq_classes, threshold=0.5, preds_type="logits"): Finds the indexes of the top peaks in the predictions.
        get_peak_boundaries(peak_info, input_data, rt_array): Gets the boundaries of the peaks.

    """

    def __init__(self, transition_group: TransitionGroup, window_size: int=175):
        super().__init__(transition_group)

        ## pad the transition group to the window size
        self.transition_group = self.transition_group.adjust_length(window_size)
        self.window_size = window_size

    @staticmethod
    def min_max_scale(data, min: float=None, max: float=None) -> np.ndarray:
        """
        Perform min-max scaling on the input data.

        Args:
            data (numpy.ndarray): The input data to be scaled.
            min (float, optional): The minimum value for scaling. If not provided, the minimum value of the data will be used.
            max (float, optional): The maximum value for scaling. If not provided, the maximum value of the data will be used.

        Returns:
            numpy.ndarray: The scaled data.

        """
        min = data.min() if not min else min
        max = data.max() if not max else max

        return np.nan_to_num((data - min) / (max - min))

    @staticmethod
    def find_thresholds(preds: np.ndarray, target: np.ndarray, min_precisions: float) -> List[tuple]:
        """
        Finds the thresholds for a given set of predictions and targets based on minimum precisions.

        Args:
            preds (numpy.ndarray): Array of predicted values.
            target (numpy.ndarray): Array of target values.
            min_precisions (float): Float of minimum precisions.

        Returns:
            list: List of tuples containing minimum precision, recall, and threshold values.
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for finding thresholds, but not installed.")
        if not TORCHMETRICS_AVAILABLE:
            raise ImportError("PyTorchMetrics is required for finding thresholds, but not installed.")
        
        preds = torch.from_numpy(preds)
        target = torch.from_numpy(target)
        thresholds = []

        for min_precision in min_precisions:
            recall, threshold = binary_recall_at_fixed_precision(
                preds, target, min_precision
            )
            thresholds.append((min_precision, recall, threshold))

        return thresholds

    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        """
        Compute the sigmoid function for the given input.

        Parameters:
        x (float): The input value.

        Returns:
        float: The sigmoid value of the input.
        """
        return 1 / (1 + np.exp(-x))

    def preprocess(self, library: SpectralLibraryLoader) -> np.ndarray:
        """
        Preprocesses the data by scaling and transforming it into a numpy array.
        
        Code adapted from CAPE

        Args:
            SpectralLibraryLoader (SpectralLibraryLoader): The spectral library loader.

        Returns:
            np.ndarray: The preprocessed data as a numpy array with shape (1, 21, len(data[0])).
        """

        # Data array ordering:
            # Row index 0-5: ms2 (sample min-max normalized)
            # Row index 6-11: ms2 (trace min-max normalized)
            # Row index 12: ms1
            # Row index 13-18: library intensity
            # Row index 19: library retention time diff
            # Row index 20: precursor charge

        if len(self.transition_group.transitionData) != 6:
            raise ValueError(f"Transition group must have 6 transitions, but has {len(self.transition_group.transitionData)}.")

        #  initialize empty numpy array
        data = np.empty((0, self.window_size), float) 
        lib_int_data = np.empty((0, self.window_size), float)

        for chrom in self.transition_group.transitionData:
            # append ms2 intensity data to data
            data = np.append(data, [chrom.intensity], axis=0)

            lib_int = library.get_fragment_library_intensity(self.transition_group.sequence, self.transition_group.precursor_charge, chrom.label)
            lib_int = np.repeat(lib_int, self.window_size)
            lib_int_data = np.append(lib_int_data, [lib_int], axis=0)

        # initialize empty numpy array to store scaled data
        new_data = np.empty((21, len(self.transition_group.transitionData[0].intensity)), float)

        ## MS2 data (sample min-max normalized)
        new_data[0:6] = self.min_max_scale(data)

        ## MS2 trace data (trace min-max normalized)
        for j in range(6, 12):
            new_data[j : j + 1] = self.min_max_scale(
                data[j - 6 : j - 5]
            )

        ## MS1 trace data
        prec_int = self.transition_group.precursorData[0].intensity
        
        # append ms1 intensity data to data
        new_data[12] = self.min_max_scale(prec_int)

        ## Library intensity data
        # append library intensity data to data
        new_data[13:19] = self.min_max_scale(lib_int_data)

        ## Library retention time diff
        # Find the middle index of the array
        middle_index = len(data[0]) // 2

        # Create a new array with the same length as the original_data
        tmp_arr = np.zeros_like(data[0], dtype=float)

        # Set the middle point to 0
        tmp_arr[middle_index] = 0

        # Increment by one on either side of the middle point
        for i in range(1, middle_index + 1):
            if middle_index - i >= 0:
                tmp_arr[middle_index - i] = i
            if middle_index + i < len(data[0]):
                tmp_arr[middle_index + i] = i

        new_data[19] = tmp_arr

        ## Add charge state
        new_data[20] = self.transition_group.precursor_charge * np.ones(len(data[0]))
        
        ## Convert to float32
        new_data = new_data.astype(np.float32)
        
        # cnvert the shape to be (1, 21, len(data[0]))
        new_data = np.expand_dims(new_data, axis=0)

        return new_data

    def find_top_peaks(self, preds, seq_classes: List[str]='input_precursor', threshold: float=0.5, preds_type: Literal['logits', 'sigmoided', 'binarized']="logits"):
        """
        Find the top peaks in the predictions.

        Args:
            preds (numpy.ndarray): The predictions.
            seq_classes (list): The sequence classes, to group the peaks by, i.e. ['precursor_id']
            threshold (float, optional): The threshold for peak detection. Defaults to 0.5.
            preds_type (str, optional): The type of predictions. Defaults to "logits". Can be one of ["logits", "sigmoided", "binarized"].

        Returns:
            dict: A dictionary containing the peak information for each sequence class.
                The dictionary has the following structure:
                {
                    "sequence_class_1": [
                        {
                            "max_idx": int,
                            "start_idx": int,
                            "end_idx": int,
                            "score": float
                        },
                        ...
                    ],
                    "sequence_class_2": [
                        ...
                    ],
                    ...
                }
        """
        peak_info = {}

        if preds_type == "logits":
            preds = self.sigmoid(preds)

        for row_idx in range(preds.shape[0]):
            if preds_type == "logits" or preds_type == "sigmoided":
                max_col_idx = np.argmax(preds[row_idx])
                score = preds[row_idx][max_col_idx]

                if preds[row_idx][max_col_idx] < threshold:
                    continue

                peak_start = max_col_idx
                peak_end = max_col_idx

                for col_idx in range(max_col_idx, -1, -1):
                    if preds[row_idx, col_idx] < preds[row_idx, max_col_idx] * 0.5:
                        peak_start = col_idx
                        break

                for col_idx in range(max_col_idx, preds.shape[1]):
                    if preds[row_idx, col_idx] < preds[row_idx, max_col_idx] * 0.5:
                        peak_end = col_idx
                        break
            elif preds_type == "binarized":
                if np.sum(preds[row_idx]) == 0:
                    continue

                try:
                    diff = np.diff(preds[row_idx])
                    peak_start = (np.where(diff == 1)[0] + 1)[0]
                    peak_end = np.where(diff == -1)[0][0]
                    max_col_idx = (peak_start + peak_end) // 2
                    score = np.inf
                except:
                    continue
            else:
                raise NotImplementedError

            if seq_classes[row_idx] in peak_info:
                peak_info[seq_classes[row_idx]].append(
                    {
                        "max_idx": max_col_idx,
                        "start_idx": peak_start,
                        "end_idx": peak_end,
                        "score": score,
                    }
                )
            else:
                peak_info[seq_classes[row_idx]] = [
                    {
                        "max_idx": max_col_idx,
                        "start_idx": peak_start,
                        "end_idx": peak_end,
                        "score": score,
                    }
                ]

        return peak_info
    
    def get_peak_boundaries(self, peak_info: dict):
        """
        Adjusts the peak boundaries in the peak_info dictionary based on the window size and the dimensions of the input rt_array.
        Calculates the actual RT values from the rt_array and appends them to the peak_info dictionary.

        Args:
            peak_info (dict): A dictionary containing information about the peaks.
            window_size (int, optional): The size of the window used for trimming the rt_array. Defaults to 175.

        Returns:
            dict: The updated peak_info dictionary with adjusted peak boundaries and RT values.
        """
        rt_array = self.transition_group.transitionData[0].data 
        if rt_array.shape[0] != self.window_size:
            print(f"input_data {rt_array.shape[0]} was trimmed to {self.window_size}, adjusting peak_info indexes to map to the original datas dimensions")
            for key in peak_info.keys():
                for i in range(len(peak_info[key])):
                    peak_info[key][i]['max_idx_org'] = peak_info[key][i]['max_idx']
                    peak_info[key][i]['start_idx_org'] = peak_info[key][i]['start_idx']
                    peak_info[key][i]['end_idx_org'] = peak_info[key][i]['end_idx']
                    new_max_idx = peak_info[key][i]['max_idx'] + (self.window_size // 2) - (rt_array.shape[0] // 2)
                    if not new_max_idx < 0:
                        peak_info[key][i]['max_idx'] = new_max_idx

                    new_start_idx = peak_info[key][i]['start_idx'] + (self.window_size // 2) - (rt_array.shape[0] // 2)
                    if not new_start_idx < 0:
                        peak_info[key][i]['start_idx'] = new_start_idx

                    peak_info[key][i]['end_idx'] = peak_info[key][i]['end_idx'] + (self.window_size // 2) - (rt_array.shape[0] // 2)

        # get actual RT value from RT array and append to peak_info
        for key in peak_info.keys():
            for i in range(len(peak_info[key])):
                peak_info[key][i]['rt_apex'] = rt_array[peak_info[key][i]['max_idx']]
                peak_info[key][i]['rt_start'] = rt_array[peak_info[key][i]['start_idx']]
                peak_info[key][i]['rt_end'] = rt_array[peak_info[key][i]['end_idx']]
                peak_info[key][i]['int_apex'] = np.max([tg.intensity[peak_info[key][i]['max_idx']] for tg in self.transition_group.transitionData])

        return peak_info