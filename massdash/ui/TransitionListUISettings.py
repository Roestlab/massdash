"""
massdash/ui/TransitionListUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
import streamlit as st
import numpy as np

class TransitionListUISettings:
    """
    Class to create the user interface for the transition list.
    
    Attributes:
        transition_list (str): A string indicating the transition list to use.
        selected_protein (str): A string indicating the selected protein.
        selected_peptide (str): A string indicating the selected peptide.
        selected_charge (str): A string indicating the selected charge.
        
    Methods:
        show_protein_selection: Displays a protein selection dropdown menu in the sidebar.
        show_peptide_selection: Displays a peptide selection dropdown menu in the
        show_charge_selection: Displays a charge selection dropdown menu in the sidebar, along with the precursor m/z value for the selected peptide and charge.
        show_library_features: Displays the library intensity, retention time, and ion mobility for the selected peptide and charge in a sidebar expander.
    """
    def __init__(self):
        """
        Initializes the TransitionListUISettings class with default values.
        """
        self.transition_list = ""
        self.selected_protein = ""
        self.selected_peptide = ""
        self.selected_charge = ""
        if 'protein_list' not in st.session_state:   
            st.session_state['protein_list'] = []

    def show_protein_selection(self, protein_list):
        """
        Displays a protein selection dropdown menu in the sidebar.

        Args:
            protein_list (list): A list of protein names to display in the dropdown menu.

        Returns:
            None
        """
        st.session_state['protein_list'] = protein_list
        col1, col2 = st.sidebar.columns([0.2, 0.95])
        with col1:
            st.write("\n\n\n\n")
            st.write("")
            if st.session_state.perf_on and st.session_state['perf_counter'] != 0:
                pick_random_protein = True
                print(f"perf_counter: {st.session_state['perf_counter']}")
                st.session_state['perf_counter'] = st.session_state['perf_counter'] - 1
                # time.sleep(1)
                if st.session_state['perf_counter'] == 0:
                    st.session_state.perf_on = False
            else:
                # Add a button to the sidebar for random protein selection
                pick_random_protein = st.button('🔀', help="Select a random protein from the list of proteins")
        with col2: 
            if pick_random_protein:
                selected_protein = np.random.choice(protein_list)
                selected_protein_index = int(np.where( [True if selected_protein==protein else False for protein in protein_list] )[0][0])
                self.selected_protein = st.selectbox(f"Select protein (of {len(st.session_state['protein_list'])} proteins)", protein_list, index=selected_protein_index, help="Select the protein to process")
            else:
                self.selected_protein = st.selectbox(f"Select protein (of {len(st.session_state['protein_list'])} proteins)", st.session_state['protein_list'], help="Select the protein to process")


    def show_peptide_selection(self, peptide_list):
        """
        Displays a peptide selection dropdown menu in the sidebar.

        Args:
            peptide_list (list): A list of peptide names to display in the dropdown menu.

        Returns:
            None
        """
        col1, col2 = st.sidebar.columns([0.2, 0.95])
        with col1:
            st.write("\n\n\n\n")
            st.write("")
            # Add a button to the sidebar for random protein selection
            pick_random_peptide = st.button('🔀', help="Select a random peptide from the list of peptides")
        with col2:
            if pick_random_peptide:
                selected_peptide = np.random.choice(peptide_list)
                selected_peptide_index = int(np.where( [True if selected_peptide==peptide else False for peptide in peptide_list] )[0][0])
                self.selected_peptide = st.selectbox(f"Select peptide (of {len(peptide_list)} peptides)", peptide_list, index=selected_peptide_index, help="Select the peptide to process")
            else:
                self.selected_peptide = st.selectbox(f"Select peptide (of {len(peptide_list)} peptides)", peptide_list, help="Select the peptide to process")
    
    def show_charge_selection(self, charge_list, transition_list):
        """
        Displays a charge selection dropdown menu in the sidebar, along with the precursor m/z value for the selected peptide and charge.

        Args:
            charge_list (list): A list of charge states to display in the dropdown menu.
            transition_list (TransitionList): A TransitionList object containing the transition data.

        Returns:
            None
        """
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.selected_charge = st.selectbox("Select charge", np.sort(charge_list), help="Select the charge state to process")
        with col2:
            precursor_mz = transition_list.get_peptide_precursor_mz(self.selected_peptide, self.selected_charge)
            st.code(f"Precursor m/z\n{precursor_mz}", language="markdown")

    def show_library_features(self, transition_list):
        """
        Displays the library intensity, retention time, and ion mobility for the selected peptide and charge in a sidebar expander.

        Args:
            transition_list (TransitionList): A TransitionList object containing the transition data.

        Returns:
            None
        """
        library_int = transition_list.get_peptide_library_intensity(self.selected_peptide, self.selected_charge)
        library_rt = transition_list.get_peptide_retention_time(self.selected_peptide, self.selected_charge)
        library_ion_mobility = transition_list.get_peptide_ion_mobility(self.selected_peptide, self.selected_charge)
        with st.sidebar.expander("Library features", expanded=False):
            st.code(f"Library intensity: {library_int}\nLibrary RT: {library_rt}\nLibrary IM: {library_ion_mobility}", language="markdown")