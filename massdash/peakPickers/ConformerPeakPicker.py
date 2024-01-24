"""
massdash/peakPickers/ConformerPeakPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from typing import List, Literal

import numpy as np

# Structs
from ..structs.TransitionGroup import TransitionGroup
from ..structs.TransitionGroupFeature import TransitionGroupFeature
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
# Utils
from ..util import check_package, LOGGER
# Transformations
from ..dataProcessing.transformations import min_max_scale, sigmoid


onnxruntime, ONNXRUNTIME_AVAILABLE = check_package("onnxruntime")
torch, TORCH_AVAILABLE = check_package("torch")
binary_recall_at_fixed_precision, TORCHMETRICS_AVAILABLE = check_package("torchmetrics", "functional.classification.binary_recall_at_fixed_precision")

class ConformerPeakPicker:
    """
    Class for performing peak picking using the Conformer model.
    
    Attributes:
        transition_group (TransitionGroup): The transition group object.
        pretrained_model_file (str): The path to the pretrained model file.
        window_size (int, optional): The window size for peak picking. Defaults to 175.
        prediction_threshold (float, optional): The prediction threshold for peak picking. Defaults to 0.5.
        prediction_type (str, optional): The prediction type for peak picking. Defaults to "logits".
        onnx_session (onnxruntime.InferenceSession): The onnx session.
        
    Methods:
        _validate_model: Validate the pretrained model is valid and an onnx model.
        load_model: Load the pretrained model.
        pick: Perform peak picking.
        _convertConformerFeatureToTransitionGroupFeatures: Convert conformer predicted feature to TransitionGroupFeatures.
    """
    
    def __init__(self, library_file: str, pretrained_model_file: str, prediction_threshold: float = 0.5, prediction_type: Literal['logits', 'sigmoided', 'binarized'] = "logits"):
        """
        Initialize the ConformerPeakPicker class.

        Args:
            pretrained_model_file (str): The path to the pretrained model file.
            prediction_threshold (float, optional): The prediction threshold for peak picking. Defaults to 0.5.
            prediction_type (str): The prediction type for peak picking. Defaults to "logits". Valid options are ["logits", "sigmoided", "binarized"].
        """
        self.pretrained_model_file = pretrained_model_file
        self.prediction_threshold = prediction_threshold
        self.prediction_type = prediction_type
        self.library = SpectralLibraryLoader(library_file)
        
        self._validate_model()

        ## set in load_model
        self.onnx_session = None
        self.window_size = None

        LOGGER.name = __class__.__name__
        
    def _validate_model(self):
        """
        Validate the pretrained model is valid and an onnx model.
        """
        if not os.path.exists(self.pretrained_model_file):
            raise ValueError(f"Pretrained model file {self.pretrained_model_file} does not exist.")
        _, file_extension = os.path.splitext(self.pretrained_model_file)
        if file_extension.lower() not in ['.onnx']:
            raise ValueError(f"Unsupported file format ({file_extension}). ConformerPeakPicker requires a .onnx file.")

    def load_model(self):
        """
        Load the pretrained model.
        """
        if not ONNXRUNTIME_AVAILABLE:
            raise ImportError("onnxruntime is required for loading the pretrained Conformer model, but not installed.")
        # Load pretrained model
        self.onnx_session = onnxruntime.InferenceSession(self.pretrained_model_file)
        if len(self.onnx_session.get_inputs()) == 0:
            raise ValueError("Pretrained model does not have any inputs.")
        elif len(self.onnx_session.get_inputs()[0].shape) != 3:
            raise ValueError("First input to model must be a 3D numpy array, current shape: {}".format(len(self.onnx_session.get_inputs()[0].shape)))
        else:
            self.window_size = self.onnx_session.get_inputs()[0].shape[2]

    def pick(self, transition_group, max_int_transition: int=1000) -> List[TransitionGroupFeature]:
        """
        Perform peak picking.

        Args:
            max_int_transition (int, optional): The maximum intensity transition. Defaults to 1000.

        Returns:
            List[TransitionGroupFeature]: The list of transition group features.
        """

        LOGGER.info("Loading model...")
        self.load_model()

        # Transform data into required input
        LOGGER.info("Preprocessing data...")
        transition_group_adjusted = transition_group.adjust_length(self.window_size) # adjust length of the transition group data to the window size
        input_data = self._preprocess(transition_group_adjusted)
        LOGGER.info("Predicting...")
        ort_input = {self.onnx_session.get_inputs()[0].name: input_data}
        ort_output = self.onnx_session.run(None, ort_input)
        LOGGER.info("Getting predicted boundaries...")
        peak_info = self._find_top_peaks(ort_output[0], ["precursor"]) 
        # Get actual peak boundaries
        peak_info = self._get_peak_boundaries(transition_group_adjusted, peak_info)
        LOGGER.info(f"Peak info: {peak_info}")
        return self._convertConformerFeatureToTransitionGroupFeatures(peak_info, max_int_transition)

    def _convertConformerFeatureToTransitionGroupFeatures(self, peak_info: dict, max_int_transition: int=1000) -> List[TransitionGroupFeature]:
        """
        Convert conformer predicted feature to TransitionGroupFeatures.

        Args:
            peak_info: The peak information.
            max_int_transition (int, optional): The maximum intensity transition. Defaults to 1000.

        Returns:
            List[TransitionGroupFeature]: The list of transition group features.
        """
        transitionGroupFeatures = []
        for ff in peak_info.values():
            f = ff[0]
            transitionGroupFeatures.append(TransitionGroupFeature(
                                            leftBoundary=f['rt_start'], 
                                            rightBoundary=f['rt_end'],
                                            areaIntensity=max_int_transition,
                                            consensusApex=f['rt_apex']))
        return transitionGroupFeatures
    
    @staticmethod
    def _find_thresholds(preds: np.ndarray, target: np.ndarray, min_precisions: float) -> List[tuple]:
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

    def _preprocess(self, transition_group) -> np.ndarray:
        """
        Preprocesses the data by scaling and transforming it into a numpy array.
        
        Code adapted from CAPE

        Args:
            transition_group (TransitionGroup): The transition group object to preprocess

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

        if len(transition_group.transitionData) != 6:
            raise ValueError(f"Transition group must have 6 transitions, but has {len(transition_group.transitionData)}.")

        #  initialize empty numpy array
        data = np.empty((0, self.window_size), float) 
        lib_int_data = np.empty((0, self.window_size), float)

        for chrom in transition_group.transitionData:
            # append ms2 intensity data to data
            data = np.append(data, [chrom.intensity], axis=0)

            lib_int = self.library.get_fragment_library_intensity(transition_group.sequence, transition_group.precursor_charge, chrom.label)
            lib_int = np.repeat(lib_int, self.window_size)
            lib_int_data = np.append(lib_int_data, [lib_int], axis=0)

        # initialize empty numpy array to store scaled data
        new_data = np.empty((21, len(transition_group.transitionData[0].intensity)), float)

        ## MS2 data (sample min-max normalized)
        new_data[0:6] = min_max_scale(data)

        ## MS2 trace data (trace min-max normalized)
        for j in range(6, 12):
            new_data[j : j + 1] = min_max_scale(
                data[j - 6 : j - 5]
            )

        ## MS1 trace data
        prec_int = transition_group.precursorData[0].intensity
        
        # append ms1 intensity data to data
        new_data[12] = min_max_scale(prec_int)

        ## Library intensity data
        # append library intensity data to data
        new_data[13:19] = min_max_scale(lib_int_data)

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
        new_data[20] = transition_group.precursor_charge * np.ones(len(data[0]))
        
        ## Convert to float32
        new_data = new_data.astype(np.float32)
        
        # cnvert the shape to be (1, 21, len(data[0]))
        new_data = np.expand_dims(new_data, axis=0)

        return new_data

    def _find_top_peaks(self, preds, seq_classes: List[str]='input_precursor'):
        """
        Find the top peaks in the predictions.

        Args:
            preds (numpy.ndarray): The predictions.
            seq_classes (list): The sequence classes, to group the peaks by, i.e. ['precursor_id']

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

        if self.prediction_type == "logits":
            preds = sigmoid(preds)

        for row_idx in range(preds.shape[0]):
            if self.prediction_type == "logits" or self.prediction_type == "sigmoided":
                max_col_idx = np.argmax(preds[row_idx])
                score = preds[row_idx][max_col_idx]

                if preds[row_idx][max_col_idx] < self.prediction_threshold:
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
            elif self.prediction_type == "binarized":
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
                raise NotImplementedError("Prediction type {} is not supported. Currently supported prediction types include [logits, sigmoided, binarized]".format(self.prediction_type))

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
    
    def _get_peak_boundaries(self, transition_group, peak_info: dict):
        """
        Adjusts the peak boundaries in the peak_info dictionary based on the window size and the dimensions of the input rt_array.
        Calculates the actual RT values from the rt_array and appends them to the peak_info dictionary.

        Args:
            peak_info (dict): A dictionary containing information about the peaks.
            window_size (int, optional): The size of the window used for trimming the rt_array. Defaults to 175.

        Returns:
            dict: The updated peak_info dictionary with adjusted peak boundaries and RT values.
        """
        rt_array = transition_group.transitionData[0].data 
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
                peak_info[key][i]['int_apex'] = np.max([tg.intensity[peak_info[key][i]['max_idx']] for tg in transition_group.transitionData])

        return peak_info