"""
massdash/peakPickers/ConformerPeakPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from typing import List

# Preprocess
from ..preprocess.ConformerPreprocessor import ConformerPreprocessor
# Structs
from ..structs.TransitionGroup import TransitionGroup
from ..structs.TransitionGroupFeature import TransitionGroupFeature
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
# Utils
from ..util import check_package
from ..util import LOGGER

onnxruntime, ONNXRUNTIME_AVAILABLE = check_package("onnxruntime")

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
    
    def __init__(self, library_file: str, pretrained_model_file: str, prediction_threshold: float = 0.5, prediction_type: str = "logits"):
        """
        Initialize the ConformerPeakPicker class.

        Args:
            transition_group (TransitionGroup): The transition group object.
            pretrained_model_file (str): The path to the pretrained model file.
            window_size (int, optional): The window size for peak picking. Defaults to 175.
            prediction_threshold (float, optional): The prediction threshold for peak picking. Defaults to 0.5.
            prediction_type (str, optional): The prediction type for peak picking. Defaults to "logits".
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
        # Transform data into required input
        LOGGER.info("Loading model...")
        self.load_model()
        LOGGER.info("Preprocessing data...")
        conformer_preprocessor = ConformerPreprocessor(transition_group, self.window_size)
        input_data = conformer_preprocessor.preprocess(self.library)
        LOGGER.info("Predicting...")
        ort_input = {self.onnx_session.get_inputs()[0].name: input_data}
        ort_output = self.onnx_session.run(None, ort_input)
        LOGGER.info("Getting predicted boundaries...")
        peak_info = conformer_preprocessor.find_top_peaks(ort_output[0], ["precursor"], self.prediction_threshold, self.prediction_type)
        # Get actual peak boundaries
        peak_info = conformer_preprocessor.get_peak_boundaries(peak_info)
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