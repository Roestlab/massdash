import os
import fnmatch
import streamlit as st
import numpy as np

# Internal modules
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
######################################
### OpenSwath File Handling

class ReadOSWFile:
    def __init__(self, osw_file_path) -> None:
        self.osw_file_path = osw_file_path
        self.osw = OSWDataAccess(osw_file_path)

@st.cache_data
def get_protein_options(protein_table):
    """
    Get a list of protein options from the provided data frame.

    Parameters:
        protein_table (pandas.DataFrame): A DataFrame containing protein data.

    Returns:
        list: A list of protein options.
    """
    return list(np.unique(protein_table.PROTEIN_ACCESSION.to_list()))

@st.cache_data
def get_peptide_options(peptide_table):
    """
    Get a list of peptide options from the provided data frame.

    Parameters:
        peptide_table (pandas.DataFrame): A DataFrame containing peptide data.

    Returns:
        list: A list of peptide options.
    """
    return list(np.unique(peptide_table.MODIFIED_SEQUENCE.to_list()))

def process_osw_file(osw_file_path):
    """
    Process an OpenSWATH results file (.osw) and display a user interface to select a protein, a peptide and a charge state.

    Parameters:
    osw_file_path (str): Path to the .osw file to process.

    Returns:
    tuple: A tuple containing the selected peptide (str), the selected precursor charge (int) and a list of dictionaries
    containing information about the transitions of the selected peptide.
    """
    # Check to ensure file exists otherwise throw error
    if not os.path.isfile(osw_file_path):
        raise ValueError(f"Error: File {osw_file_path} does not exist!")

    st.sidebar.title("Protein Selection")

    # Button to include decoys, default is False
    include_decoys = st.sidebar.checkbox("Include decoys", value=False)

    osw = OSWDataAccess(osw_file_path)

    protein_table = osw.getProteinTable(include_decoys)

    # Add a button to the sidebar for random protein selection
    pick_random_protein = st.sidebar.button('Random Protein Selection')
    if pick_random_protein:
        unique_protein_list = get_protein_options(protein_table)
        selected_protein = np.random.choice(unique_protein_list)
        selected_protein_index = int(np.where( [True if selected_protein==protein else False for protein in unique_protein_list] )[0][0])
        # print(f"Selected protein: {selected_protein} with index {selected_protein_index}")
        selected_protein_ = st.sidebar.selectbox("Select protein", get_protein_options(protein_table), index=selected_protein_index)
    else:
        # Add a searchable dropdown list to the sidebar
        selected_protein = st.sidebar.selectbox("Select protein", get_protein_options(protein_table))

    print(f"Selected protein: {selected_protein}")

    st.sidebar.title("Peptide Selection")

    # Get selected protein id from protein table based on selected protein
    selected_protein_id = protein_table[protein_table.PROTEIN_ACCESSION==selected_protein].PROTEIN_ID.to_list()[0]

    peptide_table = osw.getPeptideTableFromProteinID(selected_protein_id)

    # Add a button to the sidebar for random peptide selection
    pick_random_peptide = st.sidebar.button('Random Peptide Selection')
    if pick_random_peptide:
        unique_peptide_list = get_peptide_options(peptide_table)
        selected_peptide = np.random.choice(unique_peptide_list)
        selected_peptide_index = int(np.where( [True if selected_peptide==peptide else False for peptide in unique_peptide_list] )[0][0])
        # print(f"Selected peptide: {selected_peptide} with index {selected_peptide_index}")
        selected_peptide_ = st.sidebar.selectbox("Select peptide", get_peptide_options(peptide_table), index=selected_peptide_index)

        selected_precursor_charge = np.random.choice(osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())
        selected_precursor_charge = st.sidebar.selectbox("Select charge", osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())
    else:
        # Add a searchable dropdown list to the sidebar
        selected_peptide = st.sidebar.selectbox("Select peptide", get_peptide_options(peptide_table))

        selected_precursor_charge = st.sidebar.selectbox("Select charge", osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())

    print(f"Selected peptide: {selected_peptide} with charge {selected_precursor_charge}")

    peptide_transition_list = osw.getPeptideTransitionInfo(selected_peptide, selected_precursor_charge)
    return selected_peptide, selected_precursor_charge, peptide_transition_list

def get_sqmass_files(sqmass_file_path_input, threads=1):
    """
    Given a path to a directory or a file, returns a list of full file paths to *.sqMass files in the directory or the file itself.
    If the input path is a directory, the function displays a selection box in the sidebar to select the *.sqMass files.
    If the input path is a file, the function returns a list containing only the input file path.
    The function also displays a slider to select the number of threads to use for processing the files.
    
    Parameters:
    sqmass_file_path_input (str): Path to a directory or a file
    
    Returns:
    sqmass_file_path_list (list): List of full file paths to *.sqMass files in the directory or the file itself.
    threads (int): Number of threads to use for processing the files.
    """
    
    if os.path.isfile(sqmass_file_path_input):
        sqmass_file_path_list = [sqmass_file_path_input]
    else:
        # Check to ensure directory exists otherwise throw error
        if not os.path.isdir(sqmass_file_path_input):
            raise ValueError(f"Error: Directory {sqmass_file_path_input} does not exist!")
        
        st.sidebar.subheader("sqMass file(s)")
        with st.sidebar.expander("File list"):
            # 1. Get the list of files in the directory
            files_in_directory = os.listdir(sqmass_file_path_input)
            
            #2. Filter the files based on the *.sqMass file extension (case-insensitive)
            files_in_directory = [filename for filename in files_in_directory if fnmatch.fnmatch(filename.lower(), '*.sqmass')]

            # 3. Sort the filenames alphabetically
            sorted_filenames = sorted(files_in_directory, reverse=False)

            # Create a selection box in the sidebar
            selected_sorted_filenames = st.multiselect("sqMass files", sorted_filenames, sorted_filenames)    

            # Create a list of full file paths
            sqmass_file_path_list = [os.path.join(sqmass_file_path_input, file) for file in selected_sorted_filenames]

            if len(sqmass_file_path_list) > 1:
                    # Add Threads slider
                    st.title("Threads")
                    threads = st.slider("Number of threads", 1, os.cpu_count(), os.cpu_count())
            else:
                threads = 1
    return sqmass_file_path_list, threads

def get_mzml_files(raw_file_path_input, threads=1):
    """
    Given a path to a directory or a file, returns a list of full file paths to *.mzML files in the directory or the file itself.
    If the input path is a directory, the function displays a selection box in the sidebar to select the *.mzML files.
    If the input path is a file, the function returns a list containing only the input file path.
    The function also displays a slider to select the number of threads to use for processing the files.
    
    Parameters:
    raw_file_path_input (str): Path to a directory or a file
    
    Returns:
    raw_file_path_list (list): List of full file paths to *.mzML files in the directory or the file itself.
    threads (int): Number of threads to use for processing the files.
    """
    
    if os.path.isfile(raw_file_path_input):
        raw_file_path_list = [raw_file_path_input]
    else:
        # Check to ensure directory exists otherwise throw error
        if not os.path.isdir(raw_file_path_input):
            raise ValueError(f"Error: Directory {raw_file_path_input} does not exist!")
        
        st.sidebar.subheader("Raw file(s)")
        with st.sidebar.expander("File list"):
            # 1. Get the list of files in the directory
            files_in_directory = os.listdir(raw_file_path_input)
            
            #2. Filter the files based on the *.mzML file extension (case-insensitive)
            files_in_directory = [filename for filename in files_in_directory if fnmatch.fnmatch(filename.lower(), '*.mzml')]

            # 3. Sort the filenames alphabetically
            sorted_filenames = sorted(files_in_directory, reverse=False)

            # Create a selection box in the sidebar
            selected_sorted_filenames = st.multiselect("Raw files", sorted_filenames, sorted_filenames)

            # Create a list of full file paths
            raw_file_path_list = [os.path.join(raw_file_path_input, file) for file in selected_sorted_filenames]

            if len(raw_file_path_list) > 1:
                    # Add Threads slider
                    st.title("Threads")
                    threads = st.slider("Number of threads", 1, os.cpu_count(), os.cpu_count())
            else:
                threads = 1

    return raw_file_path_list, threads


class TransitionListUI:
    def __init__(self) -> None:
        self.transition_list = ""
        self.selected_protein = ""
        self.selected_peptide = ""
        self.selected_charge = ""
        self.qvalue_threshold = 0.01
        
        
    def show_protein_selection(self, protein_list):
        
        self.selected_protein = st.sidebar.selectbox(f"Select protein (of {len(protein_list)} proteins)", protein_list)

    def show_peptide_selection(self, peptide_list):
        self.selected_peptide = st.sidebar.selectbox(f"Select peptide (of {len(peptide_list)} peptides)", peptide_list)
    
    def show_charge_selection(self, charge_list, precursor_mz):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.selected_charge = st.selectbox("Select charge", charge_list)
        with col2:
            st.code(f"Precursor m/z\n{precursor_mz}", language="markdown")

    def show_library_features(self, transition_list):
        try:
            library_int = transition_list.get_peptide_library_intensity(self.selected_peptide, self.selected_charge)
            library_rt = transition_list.get_peptide_retention_time(self.selected_peptide, self.selected_charge)
            library_ion_mobility = transition_list.get_peptide_ion_mobility(self.selected_peptide, self.selected_charge)
            with st.sidebar.expander("Library features", expanded=False):
                st.code(f"Library intensity: {library_int}\nLibrary RT: {library_rt}\nLibrary IM: {library_ion_mobility}", language="markdown")
        except:
            with st.sidebar.expander("Library features", expanded=False):
                st.code(f"Could not find library features for the selected precursor.", language="markdown")

    def update_protein_selection(self, new_protein_list):
        # Update the available protein options
        print(f"current protein list len= {len(st.session_state['protein_list'])}")
        st.session_state['protein_list'] = new_protein_list
        print(f"new protein list len= {len(st.session_state['protein_list'])}")

        
