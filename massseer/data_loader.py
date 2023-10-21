import streamlit as st
import multiprocessing
from SqlDataAccess import SqMassDataAccess

class TraceDataLoader:
    """
    A class for loading trace data from a SqMass file.

    Attributes:
    -----------
    sqmass_file_path : str
        The file path to the SqMass file.

    Methods:
    --------
    get_precursor_trace(precursor_id)
        Returns the precursor chromatogram data and trace annotation for a given precursor ID.
    get_transitions_trace(transition_id_list, trace_annotation)
        Returns the chromatogram data and trace annotation for a list of transition IDs.
    """

    def __init__(self, sqmass_file_path):
        """
        Initializes a TraceDataLoader object.

        Parameters:
        -----------
        sqmass_file_path : str
            The file path to the SqMass file.
        """
        self.sqmass_file_path = sqmass_file_path

        self.sqmass = SqMassDataAccess(self.sqmass_file_path)

    
    def get_precursor_trace(self, precursor_id):
        """
        Returns the precursor chromatogram data and trace annotation for a given precursor ID.

        Parameters:
        -----------
        precursor_id : int
            The precursor ID.

        Returns:
        --------
        precursor_chrom_data : numpy.ndarray
            The precursor chromatogram data.
        precursor_trace_annotation : list
            The trace annotation for the precursor chromatogram.
        """
        precursor_chrom_ids = self.sqmass.getPrecursorChromIDs(precursor_id)
        precursor_chrom_data = self.sqmass.getDataForChromatograms(list(precursor_chrom_ids['chrom_ids']))
        precursor_trace_annotation = precursor_chrom_ids['native_ids']
        return precursor_chrom_data, precursor_trace_annotation


    def get_transitions_trace(self, transition_id_list, trace_annotation):
        """
        Returns the chromatogram data and trace annotation for a list of transition IDs.

        Parameters:
        -----------
        transition_id_list : list
            A list of transition IDs.
        trace_annotation : list
            The trace annotation for the transition chromatograms.

        Returns:
        --------
        chrom_data : numpy.ndarray
            The chromatogram data.
        trace_annotation : list
            The trace annotation for the chromatograms.
        """
        chrom_data = self.sqmass.getDataForChromatogramsFromNativeIds( transition_id_list )
        return chrom_data, trace_annotation

def pad_data_to_match_length(data_list, max_len):
    """
    Pads the data in the given list to match the maximum length specified.
    
    Args:
    - data_list (list): A list of tuples, where each tuple contains two lists of equal length.
                        The first list contains retention time values, and the second list contains intensity values.
    - max_len (int): The maximum length to which the data should be padded.
    
    Returns:
    - None. The function modifies the input list in place.
    """
    for i in range(len(data_list)):
        while len(data_list[i][0]) < max_len:
            data_list[i][0].append(data_list[i][0][-1] + 1)  # Pad rt with next value
            data_list[i][1].append(0)  # Pad int with 0

@st.cache_data(show_spinner=False)
def process_file(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation):
    """
    Process a file and return the data for ms1 and ms2.

    Args:
    - file_path (str): The path of the file to be processed.
    - include_ms1 (bool): Whether to include ms1 data.
    - include_ms2 (bool): Whether to include ms2 data.
    - precursor_id (str): The precursor id.
    - transition_id_list (list): The list of transition ids.
    - trace_annotation (list): The list of trace annotations.

    Returns:
    - dict: A dictionary containing the data for ms1 and ms2.
    """
    # print(f"Info: Processing file: {file_path}")
    trace_processor = TraceDataLoader(file_path)
    if include_ms1:
        precursor_chrom_data, precursor_trace_annotation = trace_processor.get_precursor_trace(precursor_id)
    else:
        precursor_chrom_data, precursor_trace_annotation = [[[]]], []
    if include_ms2:
        chrom_data, trace_annotation = trace_processor.get_transitions_trace(transition_id_list, trace_annotation)
    else:
        chrom_data, trace_annotation = [[[]]], []

    # Find the maximum length of rt, int data among both ms1 and ms2
    max_len = max(max(len(x[0]) for x in precursor_chrom_data), max(len(x[0]) for x in chrom_data))

    # Pad data to have the same length
    if include_ms1:
        pad_data_to_match_length(precursor_chrom_data, max_len)
    if include_ms2:
        pad_data_to_match_length(chrom_data, max_len)

    print(f"Returning data for file: {file_path} with ms1 rt len: {[len(x[0]) for x in precursor_chrom_data]} int len: {[len(x[0]) if len(x[0])!=0 else 0 for x in precursor_chrom_data]} and ms2 rt len: {[len(x[0]) for x in chrom_data]} int len: {[len(x[0]) if len(x[0])!=0 else 0 for x in chrom_data]}" )
    return {'ms1':[precursor_chrom_data, precursor_trace_annotation], 'ms2':[chrom_data, trace_annotation]}

@st.cache_data(show_spinner="Fetching extracted ion chromatograms...")
def process_many_files(file_path_list, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation, thread_count=-1):
    """
    Process multiple files in parallel using multiprocessing.

    Args:
        file_path_list (list): List of file paths to process.
        include_ms1 (bool): Whether to include MS1 data.
        include_ms2 (bool): Whether to include MS2 data.
        precursor_id (str): Precursor ID to extract.
        transition_id_list (list): List of transition IDs to extract.
        trace_annotation (str): Trace annotation to extract.
        thread_count (int): Number of threads to use for multiprocessing. If -1, use all available CPUs - 1.

    Returns:
        dict: A dictionary containing the output for each processed file, with the file path as the key.
    """

    if thread_count == -1:
        thread_count = multiprocessing.cpu_count() - 1

    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=thread_count)

    print(f"Info: Processing {len(file_path_list)} files with {thread_count} threads for ms1: {include_ms1} and ms2: {include_ms2} with precursor_id: {precursor_id} and transition_id_list: {transition_id_list}")

    # Process each file in parallel
    results = [pool.apply_async(process_file, args=(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation)) for file_path in file_path_list]

    output = {}
    # Wait for all processes to finish
    for file, result in zip(file_path_list, results):
        # print(f"Info: Waiting for file: {file}")
        output[file] = result.get()

    # Close the pool
    pool.close()
    pool.join()

    return output


