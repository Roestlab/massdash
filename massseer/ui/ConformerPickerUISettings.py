import os
import streamlit as st

# UI
from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings

DIRNAME = os.path.dirname(__file__)

class ConformerPickerUISettings:
    def __init__(self, main_peak_picking_settings) -> None:
        """
        Initializes a new instance of the ConformerPickerUISettings class.

        Parameters:
        -----------
        main_peak_picking_settings : PeakPickingSettings
            The peak picking settings for the main chromatogram.
        """
        self.main_peak_picking_settings = main_peak_picking_settings
        self.shipped_model = True
        self.pretrained_model_file = None
        self.conformer_window_size = 175
        self.conformer_prediction_threshold = 0.5
        self.conformer_prediction_type = "logits"

    def create_ui(self, plot_settings: ChromatogramPlotUISettings):
        """
        Creates the user interface for the ConformerPicker app.

        Parameters:
        -----------
        plot_settings : ChromatogramPlotUISettings
            The plot settings for the chromatogram.
        """
        self.shipped_model = st.sidebar.checkbox("Use shipped model", value=True, help="Use the shipped model.")
        if  self.shipped_model:
            self.pretrained_model_file = os.path.join(DIRNAME, '..', 'assets', 'models', 'conformer', 'base_cape.onnx')
            print(f"HERE: {self.pretrained_model_file}")
        else:
            self.pretrained_model_file = st.sidebar.text_input("Pretrained model file", value="", help="The pretrained model file to use.")
        
        with st.sidebar.expander("Advanced settings"):
            self.conformer_window_size = st.number_input("window size", value=175, help="The window size for the conformer model, i.e the number of points of the chromatogram.")
            self.conformer_prediction_threshold = st.number_input("prediction score threshold", value=0.2, help="The threshold for the conformer models prediction scores to find the top peak boundary.")
            self.conformer_prediction_type = st.selectbox("prediction type", options=["logits", "sigmoided", "binarized"], help="The type of prediction to use for finding the top peak.")