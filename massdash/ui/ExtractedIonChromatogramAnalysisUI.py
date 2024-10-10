"""
massdash/ui/ExtractedIonChromatogramAnalysisUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st

# Loaders
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
# UI
from .TransitionListUISettings import TransitionListUISettings

from bokeh.io import output_file
from bokeh.plotting import figure, save
import streamlit.components.v1 as components
# Current streamlit version only supports bokeh 2.4.3
# See work around: https://github.com/streamlit/streamlit/issues/5858#issuecomment-1482042533
def use_file_for_bokeh(chart: figure, chart_height=500):
    output_file('bokeh_graph.html')
    save(chart)
    with open("bokeh_graph.html", 'r', encoding='utf-8') as f:
        html = f.read()
    components.html(html, height=chart_height)
# Update the bokeh_chart method to use the file workaround
st.bokeh_chart = use_file_for_bokeh


class ExtractedIonChromatogramAnalysisUI(TransitionListUISettings):
    """
    A class representing the user interface for extracted ion chromatogram analysis.

    Inherits from TransitionListUISettings.

    Attributes:
    transition_list : SpectralLibraryLoader
        An instance of the SpectralLibraryLoader class.
    transition_settings : TransitionListUISettings
        An instance of the TransitionListUISettings class.
    target_transition_list : pd.DataFrame
        A pandas DataFrame containing the filtered transition list based on the selected protein, peptide and charge state.
    """

    def __init__(self, transition_list: SpectralLibraryLoader) -> None:
        """
         Initializes the ExtractedIonChromatogramAnalysisServer object.

        Args:
        massdash_gui : object
            An object representing the MassDash GUI.
        transition_list : object
            An object representing the transition list.
        """
        super().__init__()
        self.transition_list = transition_list
        self.transition_settings = None
        self.target_transition_list = None

    def show_transition_information(self) -> None:
        """
        Displays the transition list UI and filters the transition list based on user input.
        """
        # Create a UI for the transition list
        self.transition_settings = TransitionListUISettings()
        st.sidebar.subheader("Transition list")
        # Checkbox to include decoys (default is False)
        self.transition_settings.include_decoys = st.sidebar.checkbox("Include decoys", value=False)
        if not self.transition_settings.include_decoys:
            self.transition_list.data = self.transition_list.data[self.transition_list.data["Decoy"] == 0]
        # Slider to filter transition list by q-value
        self.transition_settings.q_value_threshold = st.sidebar.number_input(
            "Q-value threshold",
            min_value=0.0000,
            max_value=1.0000,
            value=0.0100,
            step=0.0100,
            format="%0.5f",  # Fix the format string here
            help="Filter the transition list by q-value"
        )
        self.transition_list.data = self.transition_list.data[self.transition_list.data["Qvalue"] <= self.transition_settings.q_value_threshold]
        if self.transition_list.data.empty:
            st.error("Error: No transitions passed the q-value threshold! Increase the threshold.")
            st.stop()
        # Show proteins
        self.transition_settings.show_protein_selection(self.transition_list.get_unique_proteins())
        # Show peptides for selected protein
        self.transition_settings.show_peptide_selection(self.transition_list.get_unique_peptides_per_protein(self.transition_settings.selected_protein))
        # Show charge states for selected peptide
        self.transition_settings.show_charge_selection(self.transition_list.get_unique_charge_states_per_peptide(self.transition_settings.selected_peptide), self.transition_list)
        # Show library features
        self.transition_settings.show_library_features(self.transition_list)

        # Filter the transition list based on the selected protein, peptide and charge state
        self.target_transition_list =  self.transition_list.filter_for_target_transition_list(self.transition_settings.selected_protein, self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

    def show_extracted_ion_chromatograms(self, plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_dict) -> None:
        """
        Displays the extracted ion chromatograms based on user input.

        Args:
        plot_container : st.container
            A container for the plots.
        chrom_plot_settings : ChromatogramPlotSettings
            An instance of the ChromatogramPlotSettings class.
        concensus_chromatogram_settings : ConsensusChromatogramSettings
            An instance of the ConsensusChromatogramSettings class.
        plot_dict : dict
            A dictionary containing the plot objects for each file.
        """
        if len(plot_dict.values()) == 1:
            plot_num_cols = 1
        else:
            plot_num_cols = chrom_plot_settings.num_plot_columns
        
        with plot_container:
            plot_cols = st.columns(plot_num_cols)
            col_counter = 0
            for file in plot_dict:
                plot_obj = plot_dict[file]

                if concensus_chromatogram_settings.do_consensus_chrom != 'none':
                    # TODO: implement consensus chromatogram
                    pass
                else:
                    with plot_cols[col_counter]:
                        st.plotly_chart(plot_obj)
                        col_counter+=1
                        if col_counter >= len(plot_cols):
                            col_counter = 0