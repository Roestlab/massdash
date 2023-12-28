import streamlit as st 
import random
from typing import Literal

# Internal
from massseer.ui.util import clicked

class SearchResultsAnalysisFormUI:
    """
    """
    def __init__(self) -> None:
        self.feature_file_entries = {}
    
    @staticmethod
    def add_new_row(entry_number, search_results_file_path=None, search_results_exp_name=None, search_results_file_type=None):
        cols = st.columns(spec=[0.5, 0.3, 0.2])
        search_results_file_path = cols[0].text_input("Enter file path", value=search_results_file_path, placeholder="*.osw / *.tsv", key=f"search_results_{entry_number}", help="Path to the  search results file (*.osw / *.tsv)")
        
        search_results_exp_name = cols[1].text_input("Experiment name", value=search_results_exp_name, placeholder="Experiment name", key=f"search_results_exp_name_{entry_number}", help="Name of the experiment.")
        
        if search_results_file_type is None:
            search_results_file_type = cols[2].selectbox("File type", options=["OpenSwath", "DIA-NN", "DreamDIA"], key=f"search_results_file_type_{entry_number}", help="Select the file type of the search results file.")
        elif search_results_file_type not in ["OpenSwath", "DIA-NN", "DreamDIA"] and search_results_file_type is not None:
            raise ValueError(f"search_results_file_type must be either 'OpenSwath', 'DIA-NN' or 'DreamDIA' not {search_results_file_type}")
        else:
            search_results_file_type = cols[2].selectbox("File type", options=["OpenSwath", "DIA-NN", "DreamDIA"], index=["OpenSwath", "DIA-NN", "DreamDIA"].index(search_results_file_type), key=f"search_results_file_type_{entry_number}", help="Select the file type of the search results file.")
        
        return search_results_file_path, search_results_exp_name, search_results_file_type

    def create_forum(self, st_container: Literal["st", "st.sidebar"]=st, st_type: Literal["main", "sidebar"]="main", feature_file_entries_dict=None):
        # Create form for inputting file paths and submit button
        search_results_analysis_form = st_container.form(key = f"search_results_analysis_form_{st_type}")
        with search_results_analysis_form:
            if st_type=="main":
                st.subheader("Input Search Results")
        
            input_search_container = search_results_analysis_form.container()
        
            if st_type=="main":
                cols_footer = search_results_analysis_form.columns(spec=[0.1, 0.8, 0.1])
                use_index = 2
            else:
                cols_footer = search_results_analysis_form.columns(spec=[0.6, 0.4])
                use_index = 1
            
            add_more_search_results = cols_footer[0].number_input("Add more search results", value=1, min_value=1, max_value=10, step=1, key=f'search_results_analysis_add_more_search_results_tmp_{st_type}', help="Add more search results to compare.")

            with input_search_container:
                if feature_file_entries_dict is None:
                    for i in range(1, add_more_search_results+1):
                        print(f"Adding entry {i}")
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
                submit_button = cols_footer[use_index].form_submit_button(label='Submit', help="Submit the form to begin the visualization.", use_container_width=True)
            
            if submit_button and st_type=="main":
                st.session_state.WELCOME_PAGE_STATE = False
                st.session_state.clicked['load_toy_dataset_search_results_analysis'] = False
    
    def create_ui(self):
        st.write("This workflow is designed to analyze and investigate the search results from a DIA experiment (s). and for comparisons between search results.")
        
        st.title("Search Results Analysis")
        
        load_toy_dataset = st.button('Load Search Results Analysis Example', on_click=clicked , args=['load_toy_dataset_search_results_analysis'], key='load_toy_dataset_search_results_analysis', help="Loads the search results analysis example dataset.")
        
        if load_toy_dataset:
            st.session_state.workflow = "search_results_analysis"
            st.session_state.WELCOME_PAGE_STATE = False
            
        # Create form for inputting file paths and submit button
        self.create_forum(st_container=st, st_type="main")
    