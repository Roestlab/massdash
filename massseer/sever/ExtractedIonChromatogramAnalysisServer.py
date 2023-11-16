import os
import numpy as np
import pandas as pd

import streamlit as st

# UI
from massseer.ui.ExtractedIonChromatogramAnalysisUI import ExtractedIonChromatogramAnalysisUI
from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from massseer.ui.PeakPickingUISettings import PeakPickingUISettings
from massseer.ui.ConcensusChromatogramUISettings import ConcensusChromatogramUISettings
# Loaders
from massseer.loaders.OSWDataAccess import OSWDataAccess
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.SqMassLoader import SqMassLoader
# Peak Picking
from massseer.peakPickers.pyMRMTransitionGroupPicker import pyMRMTransitionGroupPicker
from massseer.peakPickers.MRMTransitionGroupPicker import MRMTransitionGroupPicker
# Plotting
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

    def get_string_mslevels_from_bool(self, mslevel_bool_dict):
        if mslevel_bool_dict['ms1']:
            mslevel_str = 'ms1'
        elif mslevel_bool_dict['ms2']:
            mslevel_str = 'ms2'
        elif mslevel_bool_dict['ms1'] and mslevel_bool_dict['ms2']:
            mslevel_str = 'ms1ms2'
        else:
            raise ValueError('No mslevel selected')
        return mslevel_str

    def main(self):

        self.osw_data = OSWDataAccess(self.massseer_gui.file_input_settings.osw_file_path)

        self.get_transition_list()
        self.append_qvalues_to_transition_list()

        # Create a UI for the transition list
        transition_list_ui = ExtractedIonChromatogramAnalysisUI(self.massseer_gui, self.transition_list)
        transition_list_ui.show_transition_information()

        chrom_plot_settings = ChromatogramPlotUISettings(self.massseer_gui)
        chrom_plot_settings.create_sidebar()

        peak_picking_settings = PeakPickingUISettings(self.massseer_gui)
        peak_picking_settings.create_ui(chrom_plot_settings)

        concensus_chromatogram_settings = ConcensusChromatogramUISettings(self.massseer_gui)  
        concensus_chromatogram_settings.create_ui(chrom_plot_settings)    

        self.xic_data = SqMassLoader(self.massseer_gui.file_input_settings.sqmass_file_path_list, self.massseer_gui.file_input_settings.osw_file_path)

        print(f"Selected peptide: {transition_list_ui.transition_settings.selected_peptide} Selected charge: {transition_list_ui.transition_settings.selected_charge}")

        tr_group_data = self.xic_data.loadTransitionGroups(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)

          

        if peak_picking_settings.do_peak_picking == 'OSW-PyProphet':
            tr_group_feature_data = self.xic_data.loadTransitionGroupFeature(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)
        elif peak_picking_settings.do_peak_picking == 'pyPeakPickerMRM':
            if peak_picking_settings.peak_pick_on_displayed_chrom:
                mslevel = self.get_string_mslevels_from_bool({'ms1':chrom_plot_settings.include_ms1, 'ms2':chrom_plot_settings.include_ms2})
            else:
                mslevel = peak_picking_settings.mslevels
            peak_picker_param = peak_picking_settings.PeakPickerMRMParams

            tr_group_feature_data = {}
            for file, tr_group in tr_group_data.items():
                peak_picker = pyMRMTransitionGroupPicker(mslevel, peak_picker=peak_picker_param.peak_picker)
                peak_features = peak_picker.pick(tr_group)
                tr_group_feature_data[file.filename] = peak_features
        elif peak_picking_settings.do_peak_picking == 'MRMTransitionGroupPicker':
            tr_group_feature_data = {}
            for file, tr_group in tr_group_data.items():
                peak_picker = MRMTransitionGroupPicker(peak_picking_settings.smoother)
                peak_features = peak_picker.pick(tr_group)
                print(len(peak_features))
                tr_group_feature_data[file.filename] = peak_features
        else:
            tr_group_feature_data = {file.filename:None for file in tr_group_data.keys()}

        axis_limits_dict = {'x_range' : [], 'y_range' : []}
        master_rt_arr = np.concatenate([tg.flatten().rt for tg in tr_group_data.values()])
        master_int_arr = np.concatenate([tg.flatten().intensity for tg in tr_group_data.values()])

        if chrom_plot_settings.set_x_range:
            axis_limits_dict['x_range'] = [master_rt_arr.min(), master_rt_arr.max()]
        if chrom_plot_settings.set_y_range:
            axis_limits_dict['y_range'] = [0, master_int_arr.max()]

        # get the first plots x and y ranges
        first_file = list(tr_group_data.keys())[0]

        plot_obj_dict = {}
        for file, tr_group in tr_group_data.items():
            
            tr_group.targeted_transition_list = transition_list_ui.target_transition_list

            plot_settings_dict = chrom_plot_settings.get_settings()
            plot_settings_dict['x_axis_label'] = 'Retention Time (s)'
            plot_settings_dict['y_axis_label'] = 'Intensity'
            plot_settings_dict['title'] = os.path.basename(file.filename)
            plot_settings_dict['subtitle'] = f"{transition_list_ui.transition_settings.selected_protein} | {transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge}"
            if chrom_plot_settings.set_x_range and not chrom_plot_settings.link_plot_ranges:
                plot_settings_dict['x_range'] = axis_limits_dict['x_range']
            if chrom_plot_settings.set_y_range and not chrom_plot_settings.link_plot_ranges:
                plot_settings_dict['y_range'] = axis_limits_dict['y_range']
            if chrom_plot_settings.scale_intensity:
                plot_settings_dict['scale_intensity'] = chrom_plot_settings.scale_intensity

            plot_config = PlotConfig()
            plot_config.update(plot_settings_dict)

            if not tr_group.empty():
                plotter = InteractivePlotter(plot_config)
                plot_obj = plotter.plot(tr_group, tr_group_feature_data[file.filename])
                plot_obj_dict[file.filename] = plot_obj
  
        transition_list_ui.show_extracted_ion_chromatograms(chrom_plot_settings, concensus_chromatogram_settings, plot_obj_dict)


