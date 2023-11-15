import os
import pandas as pd
import streamlit as st

from massseer.ui.ExtractedIonChromatogramAnalysisUI import ExtractedIonChromatogramAnalysisUI
from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings

from massseer.loaders.OSWDataAccess import OSWDataAccess
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.SqMassLoader import SqMassLoader
from massseer.plotting.GenericPlotter import PlotConfig
from massseer.plotting.InteractivePlotter import InteractivePlotter


class ExtractedIonChromatogramAnalysisServer:
    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui
        self.transition_list = None
        self.osw_data = None
        self.xic_data = None

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

        # Create a UI for the transition list
        transition_list_ui = ExtractedIonChromatogramAnalysisUI(self.transition_list)
        transition_list_ui.show_transition_information()

        self.xic_data = SqMassLoader(self.massseer_gui.file_input_settings.sqmass_file_path_list, self.massseer_gui.file_input_settings.osw_file_path)

        print(f"Selected peptide: {transition_list_ui.transition_settings.selected_peptide} Selected charge: {transition_list_ui.transition_settings.selected_charge}")

        tr_group_data = self.xic_data.loadTransitionGroups(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)

        chrom_plot_settings = ChromatogramPlotUISettings(self.massseer_gui)
        chrom_plot_settings.create_sidebar()

        for file, tr_group in tr_group_data.items():
            print(tr_group)
            print(file.filename)

            tr_group.targeted_transition_list = transition_list_ui.target_transition_list

            print(transition_list_ui.target_transition_list.columns)

            plot_settings_dict = chrom_plot_settings.get_settings()
            plot_settings_dict['x_axis_label'] = 'Retention Time (s)'
            plot_settings_dict['y_axis_label'] = 'Intensity'
            # plot_settings_dict['title'] = os.path.basename(file.filename)
            plot_settings_dict['subtitle'] = f"{transition_list_ui.transition_settings.selected_protein} | {transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge}"
            plot_config = PlotConfig()
            plot_config.title = os.path.basename(file.filename)
            plot_config.update(plot_settings_dict)

            if not tr_group.precursorChroms[0].empty():
                plotter = InteractivePlotter(plot_config)
                plot_obj = plotter.plot(tr_group)
                st.bokeh_chart(plot_obj)
    

    