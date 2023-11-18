import streamlit as st
import os

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
            self.pretrained_model_file = os.path.join(DIRNAME, '..', 'models', 'conformer', 'base_cape.pt')
            print(f"HERE: {self.pretrained_model_file}")
        else:
            self.pretrained_model_file = st.sidebar.text_input("Pretrained model file", value="", help="The pretrained model file to use.")