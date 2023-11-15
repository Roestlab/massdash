import pandas as pd

from massseer.loaders.OSWDataAccess import OSWDataAccess
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.ui.ExtractedIonChromatogramAnalysisUI import ExtractedIonChromatogramAnalysisUI


class ExtractedIonChromatogramAnalysisServer:
    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui
        self.transition_list = None
        self.osw_data = None

    def get_transition_list(self):
        self.transition_list = SpectralLibraryLoader(self.massseer_gui.file_input_settings.osw_file_path)
        self.transition_list.load()
        print(self.transition_list.data.shape)

    def append_qvalues_to_transition_list(self):
        top_ranked_precursor_features = self.osw_data.get_top_rank_precursor_features_across_runs()
        # merge transition list with top ranked precursor features
        self.transition_list.data = pd.merge(self.transition_list.data, top_ranked_precursor_features, on=['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence', 'PrecursorMz', 'PrecursorCharge', 'Decoy'], how='left')

    def main(self):

        self.osw_data = OSWDataAccess(self.massseer_gui.file_input_settings.osw_file_path)

        self.get_transition_list()

        self.append_qvalues_to_transition_list()

        print(self.transition_list.data)

        # Create a UI for the transition list
        transition_list_ui = ExtractedIonChromatogramAnalysisUI(self.transition_list)
        transition_list_ui.show_transition_information()
    

    