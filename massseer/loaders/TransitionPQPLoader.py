from typing import List
import os
import pandas as pd
import streamlit as st

class TransitionPQPLoader:
    '''
    Class to load a transition PQP file
    '''
    REQUIRED_PQP_COLUMNS: List[str] = ['PrecursorMz', 'ProductMz', 'PrecursorCharge', 'ProductCharge',
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
    def load(_self) -> None:
        '''
        Load the transition PQP file
        '''
        # TODO: Implement the logic to load data from a PQP file
        # Probably implement a class in SqlDataAccess
        pass
    
    def _validate_columns(self) -> bool:
        '''
        Validate the PQP file has the required columns
        '''
        return all(col in self.data.columns for col in TransitionPQPLoader.REQUIRED_PQP_COLUMNS)