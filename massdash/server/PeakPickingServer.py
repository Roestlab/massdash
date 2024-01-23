"""
massdash/server/PeakPickingServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np
import streamlit as st
from typing import Literal

# UI
from ..ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ..ui.PeakPickingUISettings import PeakPickingUISettings
# Loaders
from ..loaders.SqMassLoader import SqMassLoader
# Structs
from ..structs.TransitionGroup import TransitionGroup
# Peak Picking
from ..peakPickers import pyMRMTransitionGroupPicker, MRMTransitionGroupPicker, ConformerPeakPicker
# Util
from ..util import time_block
from .util import get_string_mslevels_from_bool

class PeakPickingServer:
    """
    A class that performs peak picking on transition group data.

    Args:
        peak_picking_settings (object): The peak picking settings.
        chrom_plot_settings (object, optional): The chromatogram plot settings. Defaults to None.
    """

    def __init__(self, peak_picking_settings: PeakPickingUISettings, chrom_plot_settings: ChromatogramPlotUISettings=None):
        self.peak_picking_settings = peak_picking_settings
        self.chrom_plot_settings = chrom_plot_settings

    def perform_osw_pyprophet_peak_picking(self, xic_data: SqMassLoader, transition_list_ui: Literal['ExtractedIonChromatogramAnalysisUI', 'RawTargetedExtractionAnalysisUI']):
        """
        Performs peak picking using OSW-PyProphet algorithm.

        Args:
            xic_data (object): The XIC data.
            transition_list_ui (object): The transition list UI.

        Returns:
            dict: The transition group feature data.
        """
        with time_block() as elapsed_time:
            tr_group_feature_data = xic_data.loadTransitionGroupFeature(
                transition_list_ui.transition_settings.selected_peptide,
                transition_list_ui.transition_settings.selected_charge
            )
        st.write(f"Loading OSW-PyProphet Peak Boundaries... Elapsed time: {elapsed_time()}")
        return tr_group_feature_data

    def perform_pypeakpicker_mrm_peak_picking(self, tr_group_data: TransitionGroup):
        """
        Performs peak picking using pyPeakPickerMRM algorithm.

        Args:
            tr_group_data (dict): The transition group data.

        Returns:
            dict: The transition group feature data.
        """
        with time_block() as elapsed_time:
            if self.peak_picking_settings.peak_pick_on_displayed_chrom:
                mslevel = get_string_mslevels_from_bool(
                    {'ms1':self.chrom_plot_settings.include_ms1, 'ms2':self.chrom_plot_settings.include_ms2}
                )
            else:
                mslevel = self.peak_picking_settings.peak_picker_algo_settings.mslevels
            peak_picker_param = self.peak_picking_settings.peak_picker_algo_settings.PeakPickerMRMParams

            tr_group_feature_data = {}
            for file, tr_group in tr_group_data.items():
                peak_picker = pyMRMTransitionGroupPicker(mslevel, peak_picker=peak_picker_param.peak_picker)
                peak_features = peak_picker.pick(tr_group)
                tr_group_feature_data[file] = peak_features

        st.write(f"Performing pyPeakPickerMRM Peak Picking... Elapsed time: {elapsed_time()}")
        return tr_group_feature_data

    def perform_mrmtransitiongrouppicker_peak_picking(self, tr_group_data: TransitionGroup):
        """
        Performs peak picking using MRMTransitionGroupPicker algorithm.

        Args:
            tr_group_data (dict): The transition group data.

        Returns:
            dict: The transition group feature data.
        """
        with time_block() as elapsed_time:
            tr_group_feature_data = {}
            for file, tr_group in tr_group_data.items():
                if self.peak_picking_settings.peak_picker_algo_settings.smoother == 'none': ## none in MassDash corresponds to 'original' in MRMTransitionGroupPicker
                    peak_picker = MRMTransitionGroupPicker('original')
                else:
                    peak_picker = MRMTransitionGroupPicker(self.peak_picking_settings.peak_picker_algo_settings.smoother)
                peak_features = peak_picker.pick(tr_group)
                tr_group_feature_data[file] = peak_features

        st.write(f"Performing MRMTransitionGroupPicker Peak Picking... Elapsed time: {elapsed_time()}")
        return tr_group_feature_data

    def perform_conformer_peak_picking(self, spec_lib_path: str, tr_group_data: TransitionGroup):
        """
        Performs peak picking using ConformerPeakPicker algorithm.

        Args:
            tr_group_data (dict): The transition group data.
            spec_lib_path (str): The path to the spectral library.

        Returns:
            dict: The transition group feature data.
        """
        with time_block() as elapsed_time:
            # Peak picking using Conformer
            tr_group_feature_data = {}

            for file, tr_group in tr_group_data.items():
                #tr_group.targeted_transition_list = self.transition_list_ui.target_transition_list
                st.write(f"Pretrained model file: {self.peak_picking_settings.peak_picker_algo_settings.pretrained_model_file}")
                        
                peak_picker = ConformerPeakPicker(spec_lib_path, self.peak_picking_settings.peak_picker_algo_settings.pretrained_model_file, 
                                                  window_size=self.peak_picking_settings.peak_picker_algo_settings.conformer_window_size,
                                                  prediction_threshold=self.peak_picking_settings.peak_picker_algo_settings.conformer_prediction_threshold,
                                                  prediction_type=self.peak_picking_settings.peak_picker_algo_settings.conformer_prediction_type)
                
                # get the trantition in tr_group with the max intensity
                max_int_transition = np.max([transition.intensity for transition in tr_group.transitionData])
                peak_features = peak_picker.pick(tr_group, max_int_transition=max_int_transition)
                tr_group_feature_data[file] = peak_features
        st.write(f"Performing Conformer Peak Picking... Elapsed time: {elapsed_time()}")
        return tr_group_feature_data

    def perform_peak_picking(self, tr_group_data: TransitionGroup=None, xic_data: SqMassLoader=None, transition_list_ui: Literal['ExtractedIonChromatogramAnalysisUI', 'RawTargetedExtractionAnalysisUI']=None, spec_lib: str=None):
        """
        Performs peak picking based on the selected method.

        Args:
            tr_group_data (dict, optional): The transition group data. Defaults to None.
            xic_data (object, optional): The XIC data. Defaults to None.
            transition_list_ui (object, optional): The transition list UI. Defaults to None.
            spec_lib (object, optional): The spectral library. Defaults to None. Mandatory if peak picking using ConformerPeakPicker.

        Returns:
            dict: The transition group feature data.
        """
        tr_group_feature_data = {}
        st.write("Performing Peak Picking for", tr_group_data)

        # Perform peak picking based on the selected method
        if self.peak_picking_settings.do_peak_picking == 'OSW-PyProphet':
            tr_group_feature_data = self.perform_osw_pyprophet_peak_picking(xic_data, transition_list_ui)
        elif self.peak_picking_settings.do_peak_picking == 'pyPeakPickerMRM':
            tr_group_feature_data = self.perform_pypeakpicker_mrm_peak_picking(tr_group_data)
        elif self.peak_picking_settings.do_peak_picking == 'MRMTransitionGroupPicker':
            tr_group_feature_data = self.perform_mrmtransitiongrouppicker_peak_picking(tr_group_data)
        elif self.peak_picking_settings.do_peak_picking == 'Conformer':
            tr_group_feature_data = self.perform_conformer_peak_picking(spec_lib, tr_group_data)
        else:
            tr_group_feature_data = {file: None for file in tr_group_data.keys()}

        return tr_group_feature_data

