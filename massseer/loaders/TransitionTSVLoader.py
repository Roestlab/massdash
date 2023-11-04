from typing import List
import os
import pandas as pd
import streamlit as st

from massseer.util import get_logger

# single const instance of logger
LOGGER = get_logger(__name__)

class TransitionTSVLoader:
    '''
    Class to load a transition TSV file
    '''
    REQUIRED_TSV_COLUMNS: List[str] = ['PrecursorMz', 'ProductMz', 'PrecursorCharge', 'ProductCharge',
                                   'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence',
                                   'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'FragmentType',
                                   'FragmentSeriesNumber', 'Annotation', 'PrecursorIonMobility']
    
    def __init__(self, in_file: str) -> None:
        '''
        Constructor
        '''
        self.in_file = in_file
        self.data: pd.DataFrame = pd.DataFrame()
    
    @st.cache_data(show_spinner=False)
    def _load(_self) -> None:
        '''
        Load the transition TSV file
        '''
        LOGGER.debug(f"Loading transition TSV file {_self.in_file}")
        _self.data = pd.read_csv(_self.in_file, sep='\t')
        # Multiply the retention time by 60 to convert from minutes to seconds
        _self.data['NormalizedRetentionTime'] = _self.data['NormalizedRetentionTime'] * 60
        if _self._validate_columns():
            return _self.data
        else:
            raise ValueError(f"The TSV file does not have the required columns.\n {TransitionTSVLoader.REQUIRED_TSV_COLUMNS}")
    
    def _validate_columns(self) -> bool:
        '''
        Validate the TSV file has the required columns
        '''
        return all(col in self.data.columns for col in TransitionTSVLoader.REQUIRED_TSV_COLUMNS)