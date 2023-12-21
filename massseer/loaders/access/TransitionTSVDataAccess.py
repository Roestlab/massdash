from typing import List
import os
import pandas as pd
import streamlit as st

# Utils
from massseer.util import check_streamlit, conditional_decorator

class TransitionTSVDataAccess:
    '''
    Class to load a transition TSV file
    
    Attributes:
        filename: (str) The path to the transition TSV file.
        data: (pd.DataFrame) The TSV data.
        
    Methods:
        _load: Loads the TSV file.
        _validate_columns: Validates the TSV file has the required columns.
        _resolve_column_names: Renames the columns of the TSV file to match the required column names.
        _get_actual_column: Given an attribute name, returns the actual column name in the data that corresponds to that attribute.
        generate_annotation: Generates an annotation for each row in the data by concatenating the 'FragmentType', 'FragmentSeriesNumber', and 'ProductCharge' columns.
    '''
    REQUIRED_TSV_COLUMNS: List[str] = ['PrecursorMz', 'ProductMz', 'PrecursorCharge', 'ProductCharge',
                                   'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence',
                                   'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'FragmentType',
                                   'FragmentSeriesNumber', 'Annotation', 'PrecursorIonMobility']
    
    # Column name mapping from standardized names to possible column names
    COLUMN_NAME_MAPPING = {
        'PrecursorMz': ['precursor_mz', 'mz'],
        'ProductMz': ['product_mz'],
        'PrecursorCharge': ['precursor_charge', 'charge'],
        'ProductCharge': ['product_charge'],
        'LibraryIntensity': ['intensity'],
        'NormalizedRetentionTime': ['retention_time', 'normalized_rt'],
        'PeptideSequence': ['peptide_sequence', 'sequence'],
        'ModifiedPeptideSequence': ['modified_sequence'],
        'ProteinId': ['protein_id'],
        'GeneName': ['gene_name'],
        'FragmentType': ['fragment_type'],
        'FragmentSeriesNumber': ['fragment_series_number'],
        'Annotation': ['annotation'],
        'PrecursorIonMobility': ['ion_mobility'],
    }

    def __init__(self, filename: str) -> None:
        '''
        Constructor
        '''
        # Check that filename is of extension tsv
        _, file_extension = os.path.splitext(filename)
        if file_extension.lower() not in ['.tsv']:
            raise ValueError("Unsupported file format. TransitionTSVLoader requires a tab-separated .tsv file.")
        self.filename = filename
        self.data: pd.DataFrame = pd.DataFrame()
    
    @conditional_decorator(lambda func: st.cache_data(show_spinner=False)(func), check_streamlit())
    def _load(_self) -> None:
        '''
        Load the transition TSV file
        '''
        _self.data = pd.read_csv(_self.filename, sep='\t')
        # Multiply the retention time by 60 to convert from minutes to seconds
        _self.data['NormalizedRetentionTime'] = _self.data['NormalizedRetentionTime'] * 60
        _self._resolve_column_names()
        if 'Annotation' not in _self.data.columns:
            _self.generate_annotation()
        # Drop the FragmentType and FragmentSeriesNumber columns
        if _self._validate_columns():
            _self.data.drop(columns=['FragmentType', 'FragmentSeriesNumber'], inplace=True)
            return _self.data
        else:
            raise ValueError(f"The TSV file does not have the required columns.\n {TransitionTSVDataAccess.REQUIRED_TSV_COLUMNS}")
    
    def _resolve_column_names(self):
        """
        Renames the columns of the TSV file to match the required column names.
        If a required column is not found, it tries to find an alternative name
        for the column in the `COLUMN_NAME_MAPPING` dictionary.
        """
        for attribute_name in self.REQUIRED_TSV_COLUMNS:
            actual_column = self._get_actual_column(attribute_name)
            if actual_column is not None:
                if attribute_name not in self.data.columns:
                    self.data.rename(columns={actual_column: attribute_name}, inplace=True)
            else:
                # Check if there are alternative names for the attribute
                alternative_columns = self.COLUMN_NAME_MAPPING.get(attribute_name)
                if alternative_columns:
                    for alternative in alternative_columns:
                        if alternative in self.data.columns and attribute_name not in self.data.columns:
                            self.data.rename(columns={alternative: attribute_name}, inplace=True)

    def _get_actual_column(self, attribute_name):
            """
            Given an attribute name, returns the actual column name in the data that corresponds to that attribute.
            If no matching column is found, returns None.

            Args:
                attribute_name (str): The name of the attribute to find the corresponding column for.

            Returns:
                str or None: The name of the column in the data that corresponds to the given attribute name, or None if no matching column is found.
            """
            for possible_column_name in self.COLUMN_NAME_MAPPING.get(attribute_name, []):
                if possible_column_name in self.data.columns:
                    return possible_column_name
            return None

    def generate_annotation(self):
        """
        Generates an annotation for each row in the data by concatenating the 'FragmentType', 'FragmentSeriesNumber', and 'ProductCharge' columns.

        If the 'Annotation' column does not exist in the data, it will be created.

        Returns:
            None
        """
        if 'Annotation' not in self.data.columns:
            self.data['Annotation'] = self.data['FragmentType'] + self.data['FragmentSeriesNumber'].astype(str) + '^' + self.data['ProductCharge'].astype(str)

    def _validate_columns(self) -> bool:
        '''
        Validate the TSV file has the required columns
        '''
        return all(col in self.data.columns for col in TransitionTSVDataAccess.REQUIRED_TSV_COLUMNS)