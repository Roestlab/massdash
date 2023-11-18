import os

from typing import List

import numpy as np

try:
    import torch
    print("PyTorch is installed. Version:", torch.__version__)
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch is not installed. Please install it using 'pip install torch'.")
    TORCH_AVAILABLE = False
    # # Optionally, you can raise an error to stop the script.
    # raise ImportError("PyTorch is required for loading the pretrained Conformer model, but not installed.")

from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.preprocess.ConformerPreprocessor import ConformerPreprocessor

print(f"TORCH_AVAILABLE: {TORCH_AVAILABLE}")

class ConformerPeakPicker:
    def __init__(self, transition_group: TransitionGroup, pretrained_model_file: str, **kwargs):
        self.transition_group = transition_group
        self.pretrained_model_file = pretrained_model_file
        self.model = None
        self.kwargs = kwargs

    def load_model(self):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for loading the pretrained Conformer model, but not installed.")
        # Load pretrained model
        self.model = torch.load(self.pretrained_model_file, map_location=torch.device('cpu'))

    def pick(self) -> List[TransitionGroupFeature]:
        # Transform data into required input
        print("Preprocessing data...")
        input_data = ConformerPreprocessor(self.transition_group).preprocess()
        print("Loading model...")
        self.load_model()
        print("Predicting...")
        print(dir(self.model))
        # self.model.predict(input_data)
