from typing import List
import os
import sqlite3
import pandas as pd

import streamlit as st

from massseer.util import check_sqlite_column_in_table


class TransitionPQPLoader:
    '''
    Class to load a transition PQP file
    '''
    REQUIRED_PQP_COLUMNS: List[str] = ['PrecursorMz', 'ProductMz', 'PrecursorCharge', 'ProductCharge',
                                   'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence',
                                   'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'Annotation', 'PrecursorIonMobility']
    
    def __init__(self, filename: str) -> None:
        '''
        Constructor
        '''
        # Check that filename is either of extension .pqp or .osw
        _, file_extension = os.path.splitext(filename)
        if file_extension.lower() not in ['.pqp', '.osw']:
            raise ValueError("Unsupported file format. TransitionPQPLoader requires an sqlite-based .pqp file or .osw file.")
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
    
    @st.cache_data(show_spinner=False)
    def load(_self) -> None:
        '''
        Load the transition PQP file
        '''
        _self.data = _self.getTransitionList()
        if _self._validate_columns():
            return _self.data
        else:
            raise ValueError(f"The PQP file does not have the required columns.\n {TransitionPQPLoader.REQUIRED_PQP_COLUMNS}")
        
    def getTransitionList(self):
        """
        Retrieves transition information for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The transition information.
        """
        # Older PQP files (<v2.4) do not have the ANNOTATION column in the TRANSITION table
        if check_sqlite_column_in_table(self.conn, "PRECURSOR", "LIBRARY_DRIFT_TIME"):
            prec_lib_drift_time_query = "PRECURSOR.LIBRARY_DRIFT_TIME AS PrecursorIonMobility,"
        else:
            prec_lib_drift_time_query = "-1 AS PrecursorIonMobility,"

        if check_sqlite_column_in_table(self.conn, "TRANSITION", "ANNOTATION"):
            stmt = f"""SELECT 
                PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
                PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
                PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
                PRECURSOR.CHARGE AS PrecursorCharge,
                PRECURSOR.LIBRARY_RT AS NormalizedRetentionTime,
                {prec_lib_drift_time_query}
                TRANSITION.PRODUCT_MZ AS ProductMz,
                TRANSITION.CHARGE AS ProductCharge,
                TRANSITION.ANNOTATION AS Annotation,
                TRANSITION.LIBRARY_INTENSITY AS LibraryIntensity,
                TRANSITION.DETECTING AS PRODUCT_DETECTING,
                PRECURSOR.DECOY AS Decoy
                FROM AS PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN TRANSITION_PRECURSOR_MAPPING ON TRANSITION_PRECURSOR_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN TRANSITION ON TRANSITION.ID = TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID"""
        else:
            stmt = f"""SELECT 
                PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
                PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
                PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
                PRECURSOR.CHARGE AS PrecursorCharge,
                PRECURSOR.LIBRARY_RT AS NormalizedRetentionTime,
                {prec_lib_drift_time_query}
                TRANSITION.PRODUCT_MZ AS ProductMz,
                TRANSITION.CHARGE AS ProductCharge,
                TRANSITION.TYPE || TRANSITION.ORDINAL || '^' || TRANSITION.CHARGE AS Annotation,
                TRANSITION.LIBRARY_INTENSITY AS LibraryIntensity,
                PRECURSOR.DECOY AS Decoy
                FROM AS PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN TRANSITION_PRECURSOR_MAPPING ON TRANSITION_PRECURSOR_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN TRANSITION ON TRANSITION.ID = TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID"""

        data = pd.read_sql(stmt, self.conn)

        return data

    def _validate_columns(self) -> bool:
        '''
        Validate the PQP file has the required columns
        '''
        return all(col in self.data.columns for col in TransitionPQPLoader.REQUIRED_PQP_COLUMNS)