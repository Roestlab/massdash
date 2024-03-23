"""
massdash/ui/SearchResultsAnalysisFormUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from os.path import basename
from typing import Literal
import streamlit as st 

# UI Util
from .util import clicked, get_parent_directory, tk_file_dialog

class SearchResultsAnalysisFormUI:
    """
    """
    def __init__(self) -> None:
        self.feature_file_entries = {}
    
    @staticmethod
    def add_new_row(entry_number, search_results_file_path=None, search_results_exp_name=None, search_results_file_type=None):
        feature_file_path_entry = f'feature_file_path_{entry_number}'
        if feature_file_path_entry not in st.session_state.tmp_input_dict:
            st.session_state.tmp_input_dict[feature_file_path_entry] = None
        cols = st.columns(spec=[0.05, 0.65, 0.2, 0.1])
        with cols[0]:
            st.write("\n")
            st.write("\n\n\n\n")
            dialog_button = st.button("📁", key=f'search_results_browser_{entry_number}', help=f"Browse for the search results file.")
            if dialog_button:
                parent_dir = get_parent_directory(st.session_state.tmp_input_dict[feature_file_path_entry])
                st.session_state.tmp_input_dict[feature_file_path_entry] = tk_file_dialog(file_type=[("OpenSwath Files", ".osw"), ("Feature File", ".tsv")], title="Select Feature File", parent_dir=parent_dir)
        
        search_results_file_path = cols[1].text_input("Enter file path", value=st.session_state.tmp_input_dict[feature_file_path_entry], placeholder="*.osw / *.tsv", key=f"search_results_{entry_number}", help="Path to the  search results file (*.osw / *.tsv)")
        
        if search_results_file_path is not None:
            search_results_exp_name = basename(search_results_file_path).split(".")[0]
        
        search_results_exp_name = cols[2].text_input("Experiment name", value=search_results_exp_name, placeholder="Experiment name", key=f"search_results_exp_name_{entry_number}", help="Name of the experiment.")
        
        if search_results_file_type is None:
            search_results_file_type = cols[3].selectbox("File type", options=["OpenSWATH", "DIA-NN", "DreamDIA"], key=f"search_results_file_type_{entry_number}", help="Select the file type of the search results file.")
        elif search_results_file_type not in ["OpenSWATH", "DIA-NN", "DreamDIA"] and search_results_file_type is not None:
            raise ValueError(f"search_results_file_type must be either 'OpenSWATH', 'DIA-NN' or 'DreamDIA' not {search_results_file_type}")
        else:
            search_results_file_type = cols[3].selectbox("File type", options=["OpenSWATH", "DIA-NN", "DreamDIA"], index=["OpenSWATH", "DIA-NN", "DreamDIA"].index(search_results_file_type), key=f"search_results_file_type_{entry_number}", help="Select the file type of the search results file.")
        
        return search_results_file_path, search_results_exp_name, search_results_file_type

    def create_forum(self, st_container: Literal["st", "st.sidebar"]=st, st_type: Literal["main", "sidebar"]="main", feature_file_entries_dict=None):
        # Create form for inputting file paths and submit button
        if st_type=="main":
            st.subheader("Input Search Results")
            
        input_area_container = st_container.container(border=True)
        
        if st_type=="main":
            cols_footer = st_container.columns(spec=[0.1, 0.8, 0.1])
            use_index = 2
        else:
            cols_footer = st_container.columns(spec=[0.6, 0.4])
            use_index = 1
        
        add_more_search_results = cols_footer[0].number_input("Add more search results", value=1, min_value=1, max_value=10, step=1, key=f'search_results_analysis_add_more_search_results_tmp_{st_type}', help="Add more search results to compare.")
        
        with input_area_container:
            if feature_file_entries_dict is None:
                for i in range(1, add_more_search_results+1):
                    search_results_file_path, search_results_exp_name, search_results_file_type = self.add_new_row(f"entry_{st_type}_{str(i)}")
                    self.feature_file_entries[f"entry_{str(i)}"] = {'search_results_file_path':search_results_file_path, 'search_results_exp_name':search_results_exp_name, 'search_results_file_type':search_results_file_type}
            else:
                for key, value in feature_file_entries_dict.items():
                    search_results_file_path, search_results_exp_name, search_results_file_type = self.add_new_row(key, value['search_results_file_path'], value['search_results_exp_name'], value['search_results_file_type'])
                    self.feature_file_entries[key] = {'search_results_file_path':search_results_file_path, 'search_results_exp_name':search_results_exp_name, 'search_results_file_type':search_results_file_type}
        
        if st_type=="main":
            cols_footer[1].empty()
        with cols_footer[use_index]:
            st.write("\n\n\n\n")
            st.write("")
            submit_button = cols_footer[use_index].button(label='Submit', help="Submit the form to begin the visualization.", use_container_width=True, key=f"st_type_{st_type}")
        
        if submit_button and st_type=="main":
            st.session_state.WELCOME_PAGE_STATE = False
            st.session_state.clicked['load_toy_dataset_search_results_analysis'] = False
            st.session_state.workflow = "search_results_analysis"
    
    def create_ui(self, isStreamlitCloud: bool = False):
        st.title("Search Results Analysis")
        st.write("This workflow is designed to analyze and investigate the search results from a DIA experiment(s) and for comparisons between search results.")

        load_toy_dataset = st.button('Load Search Results Analysis Example', on_click=clicked , args=['load_toy_dataset_search_results_analysis'], key='load_toy_dataset_search_results_analysis', help="Loads the search results analysis example dataset.")
        
        if load_toy_dataset:
            st.session_state.workflow = "search_results_analysis"
            st.session_state.WELCOME_PAGE_STATE = False
            
        if not isStreamlitCloud:
            # Create form for inputting file paths and submit button
            self.create_forum(st_container=st, st_type="main")
    