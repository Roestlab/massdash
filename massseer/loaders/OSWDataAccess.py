#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
=========================================================================
            MassSeer 
=========================================================================

Copyright (c) 2013, ETH Zurich
For a full list of authors, refer to the file AUTHORS.

This software is released under a three-clause BSD license:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of any author or any participating institution
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
--------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
$Maintainer: Justin Sing$
$Authors: Hannes Roest, Justin Sing$
--------------------------------------------------------------------------
"""
import pandas as pd
import sqlite3
from massseer.util import check_sqlite_column_in_table, check_sqlite_table

class OSWDataAccess:
    """
    A class for accessing data from an OpenSWATH SQLite database.

    Attributes:
        conn (sqlite3.Connection): A connection to the SQLite database.
        c (sqlite3.Cursor): A cursor for executing SQL statements on the database.
    """

    def __init__(self, filename):
        """
        Initializes a new instance of the OSWDataAccess class.

        Args:
            filename (str): The path to the SQLite database file.
        """
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def getProteinTable(self, include_decoys=False):
        """
        Retrieves the protein table from the database.

        Args:
            include_decoys (bool): Whether to include decoy proteins in the table.

        Returns:
            pandas.DataFrame: The protein table.
        """
        if include_decoys:
            stmt = "SELECT PROTEIN_ID, PEPTIDE_ID, PROTEIN_ACCESSION, PROTEIN.DECOY FROM PROTEIN INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = PROTEIN.ID INNER JOIN PEPTIDE ON PEPTIDE.ID = PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID"
        else:
            stmt = "SELECT PROTEIN_ID, PEPTIDE_ID, PROTEIN_ACCESSION, PROTEIN.DECOY FROM PROTEIN INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = PROTEIN.ID INNER JOIN PEPTIDE ON PEPTIDE.ID = PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID WHERE PROTEIN.DECOY = 0"

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPeptideTable(self, remove_ipf_peptides=True):
        """
        Retrieves the peptide table from the database.

        Args:
            remove_ipf_peptides (bool): Whether to remove IPF peptides from the table.

        Returns:
            pandas.DataFrame: The peptide table.
        """
        if remove_ipf_peptides:
            stmt = """SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID"""
        else:   
            stmt ="SELECT * FROM PEPTIDE"

        data = pd.read_sql(stmt, self.conn)

        return data

    # Method to get peptide table from protein_id
    def getPeptideTableFromProteinID(self, protein_id, remove_ipf_peptide=True):
        """
        Retrieves the peptide table from the database for a given protein ID.

        Args:
            protein_id (int): The protein ID.
            remove_ipf_peptides (bool): Whether to remove IPF peptides from the table.

        Returns:
            pandas.DataFrame: The peptide table.
        """
        if remove_ipf_peptide:
            stmt = f"""SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        WHERE PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = {protein_id}"""
        else:
            stmt = f"""SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        WHERE PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = {protein_id}"""

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPrecursorCharges(self, fullpeptidename):
        """
        Retrieves the precursor charges for a given peptide.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.

        Returns:
            pandas.DataFrame: The precursor charges.
        """
        stmt = f"SELECT CHARGE FROM PRECURSOR INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID INNER JOIN (SELECT * FROM PEPTIDE WHERE PEPTIDE.MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID"

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPeptideTransitionInfo(self, fullpeptidename, charge):
        """
        Retrieves transition information for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The transition information.
        """
        # Older OSW files (<v2.4) do not have the ANNOTATION column in the TRANSITION table
        if check_sqlite_column_in_table(self.conn, "PRECURSOR", "LIBRARY_DRIFT_TIME"):
            prec_lib_drift_time_query = "PRECURSOR.LIBRARY_DRIFT_TIME AS PRECURSOR_LIBRARY_DRIFT_TIME,"
        else:
            prec_lib_drift_time_query = "-1 AS PRECURSOR_LIBRARY_DRIFT_TIME,"

        if check_sqlite_column_in_table(self.conn, "TRANSITION", "ANNOTATION"):
            stmt = f"""SELECT 
                PEPTIDE.ID AS PEPTIDE_ID,
                PRECURSOR.ID AS PRECURSOR_ID,
                TRANSITION.ID AS TRANSITION_ID,
                PEPTIDE.UNMODIFIED_SEQUENCE,
                PEPTIDE.MODIFIED_SEQUENCE,
                PRECURSOR.PRECURSOR_MZ,
                PRECURSOR.CHARGE AS PRECURSOR_CHARGE,
                PRECURSOR.LIBRARY_INTENSITY AS PRECURSOR_LIBRARY_INTENSITY,
                PRECURSOR.LIBRARY_RT AS PRECURSOR_LIBRARY_RT,
                {prec_lib_drift_time_query}
                TRANSITION.PRODUCT_MZ,
                TRANSITION.CHARGE AS PRODUCT_CHARGE,
                TRANSITION.TYPE AS PRODUCT_TYPE,
                TRANSITION.ORDINAL AS PRODUCT_ORDINAL,
                TRANSITION.ANNOTATION AS PRODUCT_ANNOTATION,
                TRANSITION.LIBRARY_INTENSITY AS PRODUCT_LIBRARY_INTENSITY,
                TRANSITION.DETECTING AS PRODUCT_DETECTING,
                PEPTIDE.DECOY AS PEPTIDE_DECOY,
                PRECURSOR.DECOY AS PRECURSOR_DECOY,
                TRANSITION.DECOY AS TRANSITION_DECOY
                FROM (SELECT * FROM PRECURSOR WHERE PRECURSOR.CHARGE = {charge}) AS PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN (SELECT * FROM PEPTIDE WHERE PEPTIDE.MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN TRANSITION_PRECURSOR_MAPPING ON TRANSITION_PRECURSOR_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN TRANSITION ON TRANSITION.ID = TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID"""
        else:
            stmt = f"""SELECT 
                PEPTIDE.ID AS PEPTIDE_ID,
                PRECURSOR.ID AS PRECURSOR_ID,
                TRANSITION.ID AS TRANSITION_ID,
                PEPTIDE.UNMODIFIED_SEQUENCE,
                PEPTIDE.MODIFIED_SEQUENCE,
                PRECURSOR.PRECURSOR_MZ,
                PRECURSOR.CHARGE AS PRECURSOR_CHARGE,
                PRECURSOR.LIBRARY_INTENSITY AS PRECURSOR_LIBRARY_INTENSITY,
                PRECURSOR.LIBRARY_RT AS PRECURSOR_LIBRARY_RT,
                {prec_lib_drift_time_query}
                TRANSITION.PRODUCT_MZ,
                TRANSITION.CHARGE AS PRODUCT_CHARGE,
                TRANSITION.TYPE AS PRODUCT_TYPE,
                TRANSITION.ORDINAL AS PRODUCT_ORDINAL,
                TRANSITION.TYPE || TRANSITION.ORDINAL || '^' || TRANSITION.CHARGE AS PRODUCT_ANNOTATION,
                TRANSITION.LIBRARY_INTENSITY AS PRODUCT_LIBRARY_INTENSITY,
                TRANSITION.DETECTING AS PRODUCT_DETECTING,
                PEPTIDE.DECOY AS PEPTIDE_DECOY,
                PRECURSOR.DECOY AS PRECURSOR_DECOY,
                TRANSITION.DECOY AS TRANSITION_DECOY
                FROM (SELECT * FROM PRECURSOR WHERE PRECURSOR.CHARGE = {charge}) AS PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN (SELECT * FROM PEPTIDE WHERE PEPTIDE.MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN TRANSITION_PRECURSOR_MAPPING ON TRANSITION_PRECURSOR_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN TRANSITION ON TRANSITION.ID = TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID"""

        data = pd.read_sql(stmt, self.conn)

        return data

    def getRunPrecursorPeakBoundaries(self, run_basename_wo_ext, fullpeptidename, charge):

        if check_sqlite_table(self.conn, "SCORE_MS2"):
            join_score_ms2 = "INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID"
            select_score_ms2 = """SCORE_MS2.SCORE AS ms2_dscore,
                SCORE_MS2.RANK AS peakgroup_rank,
                SCORE_MS2.QVALUE AS ms2_mscore,"""
        else:
            join_score_ms2 = ""
            select_score_ms2 = ""
        
        if check_sqlite_column_in_table(self.conn, "FEATURE", "EXP_IM"):
            select_feature_exp_im = "FEATURE.EXP_IM AS IM,"
        else:
            select_feature_exp_im = "-1 AS IM,"
        
        stmt = f"""SELECT 
                PEPTIDE.MODIFIED_SEQUENCE AS FullPeptideName,
                PRECURSOR.CHARGE AS Charge,
                FEATURE.ID AS feature_id,
                FEATURE_MS2.APEX_INTENSITY AS Intensity,
                FEATURE.EXP_RT AS RT,
                FEATURE.LEFT_WIDTH AS leftWidth,
                FEATURE.RIGHT_WIDTH AS rightWidth,
                {select_feature_exp_im}
                {select_score_ms2}
                PRECURSOR.DECOY AS decoy
                FROM (SELECT * FROM PRECURSOR WHERE CHARGE = {charge}) AS PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN (SELECT * FROM PEPTIDE WHERE MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                INNER JOIN (SELECT * FROM RUN WHERE FILENAME LIKE '%{run_basename_wo_ext}%') AS RUN ON RUN.ID = FEATURE.RUN_ID
                {join_score_ms2}"""

        data = pd.read_sql(stmt, self.conn)

        return data
    
    def get_top_rank_precursor_features_across_runs(self):
        """
        Retrieves the top ranking precursor features across runs from the database.

        Returns:
            pandas.DataFrame: The top ranking precursor features.
        """
        stmt = """SELECT 
                RUN.FILENAME as filename,
                PROTEIN.PROTEIN_ACCESSION AS ProteinId,
                PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
                PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
                PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
                PRECURSOR.CHARGE AS PrecursorCharge,
                PRECURSOR.DECOY AS Decoy,
                MIN(DISTINCT SCORE_MS2.QVALUE) as Qvalue
                FROM FEATURE
                INNER JOIN RUN ON RUN.ID = FEATURE.RUN_ID
                INNER JOIN (SELECT * FROM SCORE_MS2 WHERE SCORE_MS2.RANK = 1) AS SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                INNER JOIN PRECURSOR ON PRECURSOR.ID = FEATURE.PRECURSOR_ID
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                INNER JOIN PROTEIN ON PROTEIN.ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                GROUP BY ProteinId, PeptideSequence, ModifiedPeptideSequence, PrecursorMz, PrecursorCharge;"""

        data = pd.read_sql(stmt, self.conn)

        return data
