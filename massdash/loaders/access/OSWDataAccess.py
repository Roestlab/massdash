"""
massdash/loaders/access/OSWDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
=========================================================================
            MassDash 
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
import sqlite3
import pandas as pd
from typing import List, Literal, Optional, Dict, Union, Callable
from pathlib import Path
from functools import lru_cache

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import check_sqlite_column_in_table, check_sqlite_table, LOGGER

class OSWDataAccess(GenericResultsAccess):
    """
    A class for accessing data from an OpenSWATH SQLite database.

    Attributes:
        conn (sqlite3.Connection): A connection to the SQLite database.
        c (sqlite3.Cursor): A cursor for executing SQL statements on the database.
        verbose (bool): Whether to print verbose output.
        mode (str): The mode to use when intiating the data access object, to control which attributes get initialized.
    """

    def __init__(self, *args, mode: Literal['module', 'gui'] = 'module', **kwargs): 
        """
        Initializes a new instance of the OSWDataAccess class.

        Args:
            filename (str): The path to the SQLite database file.
        """
        super().__init__(*args, **kwargs)
        self.conn = sqlite3.connect(self.filename, check_same_thread=False)
        self.c = self.conn.cursor()
        
        # hashtable, each run is its own data 
        self._initializePeptideHashtable()
        self._initializeRunHashtable()
        self._initializeValidScores()
        self._initializeFeatureScoreHashtable()
        
        if mode == 'gui':
            self.df = self.load_data()
    
    @property
    @lru_cache(maxsize=None) # cache so only computed once
    def has_im(self) -> bool:
        # Check if EXP_IM in FEATURE table
        return check_sqlite_column_in_table(self.conn, "FEATURE", "EXP_IM")
    
    @property
    @lru_cache(maxsize=None) # cache so only computed once
    def has_SCORE_MS2(self) -> bool:
        return check_sqlite_table(self.conn, "SCORE_MS2")
    
    @property
    @lru_cache(maxsize=None) # cache so only computed once
    def has_SCORE_PEPTIDE(self) -> bool:
        return check_sqlite_table(self.conn, "SCORE_PEPTIDE")
    
    @property
    @lru_cache(maxsize=None) # cache so only computed once
    def has_SCORE_PROTEIN(self) -> bool:
        return check_sqlite_table(self.conn, "SCORE_PROTEIN")

    ###### INDICES CREATOR ######
    def _initialize_indices(self):
        # Create indices if they do not exist
        idx_query = ''' CREATE INDEX IF NOT EXISTS idx_transition_precursor_mapping_transition_id on TRANSITION_PRECURSOR_MAPPING(Transition_id);'''
        idx_query += ''' CREATE INDEX IF NOT EXISTS idx_transition_precursor_mapping_precursor_id on TRANSITION_PRECURSOR_MAPPING(Precursor_id);'''
        idx_query += ''' CREATE INDEX IF NOT EXISTS idx_feature_precursor_id ON FEATURE (PRECURSOR_ID); '''
        self.conn.executescript(idx_query)

    ###### HASHTABLE INITIALIZERS ######
    def _initializeRunHashtable(self):
        stmt = "select * from run"
        self.runHashTable = pd.read_sql(stmt, self.conn)
        self.runHashTable['RUN_NAME'] = self.runHashTable['FILENAME'].apply(lambda x: Path(x).stem)

    def _initializePeptideHashtable(self):
        stmt = '''
            SELECT MODIFIED_SEQUENCE, CHARGE, PRECURSOR_ID 
            FROM PRECURSOR
            INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID'''
        tmp = pd.read_sql(stmt, self.conn)
        self.peptideHash = tmp.set_index(['MODIFIED_SEQUENCE', 'CHARGE'])
    
    def _initializeFeatureScoreHashtable(self):
        if self.has_SCORE_MS2: 
            join_score_ms2 = "INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID"
            select_score_ms2 = """SCORE_MS2.RANK AS peakgroup_rank,
SCORE_MS2.QVALUE AS ms2_mscore,"""
        else:
            join_score_ms2 = ""
            select_score_ms2 = ""
                       
        stmt = f"""
        SELECT FEATURE.ID AS FEATURE_ID,
        {select_score_ms2}
        FEATURE.PRECURSOR_ID,
        PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID,
        PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID,
        FEATURE.RUN_ID
        FROM FEATURE
        {join_score_ms2}
        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = FEATURE.PRECURSOR_ID
        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
        """
        tmp = pd.read_sql(stmt, self.conn)
        
        extra_scores_dfs = {}
        # augment with peptide, protein and gene scores if available
        if self.has_SCORE_PEPTIDE:
            stmt = "SELECT CONTEXT, RUN_ID, PEPTIDE_ID, QVALUE FROM SCORE_PEPTIDE WHERE CONTEXT != 'global'"
            tmp_tbl = pd.read_sql(stmt, self.conn)
            if self.c.execute("SELECT CONTEXT FROM SCORE_PEPTIDE WHERE CONTEXT == 'global'").fetchone() is not None:
                tmp_tbl_global = pd.read_sql("SELECT PEPTIDE_ID, QVALUE FROM SCORE_PEPTIDE WHERE CONTEXT == 'global'", self.conn)
                # Rename column  to "SCORE_global", "PVALUE_global", "QVALUE_global", "PEP_global"
                tmp_tbl_global.rename(columns={'QVALUE': 'PEPTIDE_QVALUE_global'}, inplace=True)
            else:
                tmp_tbl_global = pd.DataFrame(columns=['PEPTIDE_ID', 'PEPTIDE_QVALUE_global'])

            pivoted_tbl = tmp_tbl.pivot_table(
                                                index=['RUN_ID', 'PEPTIDE_ID'],
                                                columns='CONTEXT',
                                                values=['QVALUE']
                                            ).reset_index()
                        
            # Flatten the MultiIndex columns
            pivoted_tbl.columns = [ "PEPTIDE_" + col[0] + "_" + col[1] if col[1] != "" else col[0] for col in pivoted_tbl.columns.values ]

            # # Rename columns to match the desired format
            # pivoted_tbl.rename(columns={'PEPTIDE_ID_': 'PEPTIDE_ID'}, inplace=True)

            # Merge pivoted_tbl with tmp_tbl_global
            tmp_tbl = pd.merge(pivoted_tbl, tmp_tbl_global, on=['PEPTIDE_ID'], how='left')
            extra_scores_dfs["PEPTIDE_ID"] =  tmp_tbl
        
        if self.has_SCORE_PROTEIN: 
            stmt = "SELECT CONTEXT, RUN_ID, PROTEIN_ID, QVALUE  FROM SCORE_PROTEIN WHERE CONTEXT != 'global'"
            tmp_tbl = pd.read_sql(stmt, self.conn)
            if self.c.execute("SELECT CONTEXT FROM SCORE_PROTEIN WHERE CONTEXT == 'global'").fetchone() is not None:
                tmp_tbl_global = pd.read_sql("SELECT PROTEIN_ID, QVALUE FROM SCORE_PROTEIN WHERE CONTEXT == 'global'", self.conn)
                # Rename columns to "SCORE_global", "PVALUE_global", "QVALUE_global", "PEP_global"
                tmp_tbl_global.rename(columns={'SCORE': 'PROTEIN_SCORE_global', 'PVALUE': 'PROTEIN_PVALUE_global', 'QVALUE': 'PROTEIN_QVALUE_global', 'PEP': 'PROTEIN_PEP_global'}, inplace=True)
            else:
                tmp_tbl_global = pd.DataFrame(columns=['PROTEIN_ID', 'PROTEIN_QVALUE_global'])

            pivoted_tbl = tmp_tbl.pivot_table(
                                                index=['RUN_ID', 'PROTEIN_ID'],
                                                columns='CONTEXT',
                                                values=['QVALUE']
                                            ).reset_index()
                        
            # Flatten the MultiIndex columns
            pivoted_tbl.columns = [ "PROTEIN_" + col[0] + "_" + col[1] if col[1] != "" else col[0] for col in pivoted_tbl.columns.values ]

            # # Rename columns to match the desired format
            # pivoted_tbl.rename(columns={'PROTEIN_ID_': 'PROTEIN_ID'}, inplace=True)

            # Merge pivoted_tbl with tmp_tbl_global
            tmp_tbl = pd.merge(pivoted_tbl, tmp_tbl_global, on=['PROTEIN_ID'], how='left')
            extra_scores_dfs['PROTEIN_ID'] = tmp_tbl
        
        if len(extra_scores_dfs) > 0:
            if check_sqlite_table(self.conn, "SCORE_PEPTIDE"):
                tmp = pd.merge(tmp, extra_scores_dfs['PEPTIDE_ID'], on=['RUN_ID', 'PEPTIDE_ID'], how='left')
            if check_sqlite_table(self.conn, "SCORE_PROTEIN"):
                tmp = pd.merge(tmp, extra_scores_dfs['PROTEIN_ID'], on=['RUN_ID', 'PROTEIN_ID'], how='left')
        
        self.featureScoreHash = tmp.set_index(['FEATURE_ID', 'PRECURSOR_ID', 'PEPTIDE_ID', 'PROTEIN_ID', 'RUN_ID'])

    ###### INTERNAL ACCESSORS ######
    def _getFeaturesFromPrecursorIdAndRunDf(self, run_id: str, precursor_id: int) -> pd.DataFrame:
        if check_sqlite_table(self.conn, "SCORE_MS2"):
            join_score_ms2 = "INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID"
            select_score_ms2 = """SCORE_MS2.SCORE AS ms2_dscore,
                SCORE_MS2.RANK AS peakgroup_rank,
                SCORE_MS2.QVALUE AS ms2_mscore,"""
        else:
            join_score_ms2 = ""
            select_score_ms2 = ""

        if check_sqlite_table(self.conn, "SCORE_IPF"):
            join_score_ipf = "INNER JOIN SCORE_IPF ON SCORE_IPF.FEATURE_ID = FEATURE.ID"
            select_score_ipf = """SCORE_IPF.QVALUE AS ipf_mscore,"""
        else:
            join_score_ipf = ""
            select_score_ipf = ""
        
        if self.has_im: 
            select_feature_exp_im = "FEATURE.EXP_IM AS IM,"
        else:
            select_feature_exp_im = "-1 AS IM,"
        
        stmt = f"""SELECT 
                FEATURE.ID AS feature_id,
                FEATURE.PRECURSOR_ID as PRECURSOR_ID,
                PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
                PRECURSOR.CHARGE AS Charge,
                FEATURE_MS2.AREA_INTENSITY AS areaIntensity,
                FEATURE_MS2.APEX_INTENSITY AS apexIntensity,
                PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
                FEATURE.EXP_RT AS RT,
                FEATURE.LEFT_WIDTH AS leftWidth,
                FEATURE.RIGHT_WIDTH AS rightWidth,
                {select_feature_exp_im}
                {select_score_ms2}
                {select_score_ipf}
                RUN_ID
                FROM FEATURE
                INNER JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                INNER JOIN RUN ON RUN.ID = FEATURE.RUN_ID
                INNER JOIN PRECURSOR ON PRECURSOR.ID = FEATURE.PRECURSOR_ID
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                {join_score_ms2}
                {join_score_ipf}
                WHERE RUN_ID = {run_id} AND FEATURE.PRECURSOR_ID = {precursor_id}
                """

        out = pd.read_sql(stmt, self.conn)
        out = out.rename(columns={'leftWidth': 'leftBoundary', 
                                    'rightWidth': 'rightBoundary', 
                                    'Intensity': 'areaIntensity', 
                                    'apexIntensity' : 'consensusApexIntensity',
                                    'RT': 'consensusApex', 
                                    'ms2_mscore' : 'qvalue',
                                    'Charge': 'precursor_charge',
                                    'ModifiedPeptideSequence': 'sequence',
                                    'PrecursorMz': 'precursor_mz',
                                    'IM': 'consensusApexIM',
                                    'PRECURSOR_ID': 'precursor_id',
                                    'RUN_ID': 'run_id'})
        out['software'] = 'OpenSWATH'
        return out
    
    def _getFeaturesFromPrecursorIdAndRun(self, run_id: str, precursor_id: int) -> List[TransitionGroupFeature]:
        df = self._getFeaturesFromPrecursorIdAndRunDf(run_id, precursor_id)
        out = []
        for _, i in df.iterrows():
            out.append(TransitionGroupFeature(i['leftBoundary'], 
                                              i['rightBoundary'], 
                                              areaIntensity=i['areaIntensity'], 
                                              consensusApex=i['consensusApex'],
                                              qvalue= i['ipf_mscore'] if 'ipf_mscore' in i else i['qvalue'], 
                                              precursor_charge=i['precursor_charge'], 
                                              sequence=i['sequence'], 
                                              consensusApexIntensity=i['consensusApexIntensity'],
                                              consensusApexIM=i['consensusApexIM'],
                                              software='OpenSWATH')) # will be -1 if IM is not present
        return out
    
    def _getTopFeatureFromPrecursorIdAndRun(self, run_id: str, precursor_id: int) -> List[TransitionGroupFeature]:
        df = self._getFeaturesFromPrecursorIdAndRunDf(run_id, precursor_id)
        if 'peakgroup_rank' in df.columns:
            df = df[df['peakgroup_rank'] == 1].iloc[0]
        else:
            raise ValueError("SCORE_MS2 table not found, cannot get top feature")
        return TransitionGroupFeature(df['leftBoundary'], 
                                            df['rightBoundary'], 
                                            areaIntensity=df['consensusApexIntensity'], 
                                            qvalue= df['ipf_mscore'] if 'ipf_mscore' in df else df['qvalue'], 
                                            precursor_charge=df['precursor_charge'], 
                                            sequence=df['sequence'], 
                                            consensusApex=df['consensusApex'],
                                            consensusApexIntensity=df['consensusApexIntensity'],
                                            consensusApexIM=df['consensusApexIM'],
                                            software='OpenSWATH') # will be -1 if IM is not present
 
    def _getTopFeatureFromPrecursorIdAndRunDf(self, run_id: str, precursor_id: int) -> List[TransitionGroupFeature]:
        df = self._getFeaturesFromPrecursorIdAndRunDf(run_id, precursor_id)
        df = df.rename(columns={'leftWidth': 'leftBoundary', 
                                    'rightWidth': 'rightBoundary', 
                                    'Intensity': 'consensusApexIntensity', 
                                    'RT': 'consensusApex', 
                                    'ms2_mscore' : 'qvalue',
                                    'Charge': 'precursor_charge',
                                    'ModifiedPeptideSequence': 'sequence',
                                    'PrecursorMz': 'precursor_mz',
                                    'IM': 'consensusApexIM',
                                    'PRECURSOR_ID': 'precursor_id',
                                    'RUN_ID': 'run_id'})
        
        if 'peakgroup_rank' in df.columns:
            return df[df['peakgroup_rank'] == 1].iloc[[0]]
        else:
            raise ValueError("SCORE_MS2 table not found, cannot get top feature")

    def _getTransitionsFromPrecursorId(self, precursor_id:int) -> pd.DataFrame:
        '''
        Initialize the which maps peptide precursor to its ID
        '''
        # Older OSW files (<v2.4) do not have the ANNOTATION column in the TRANSITION table
        if check_sqlite_column_in_table(self.conn, "TRANSITION", "ANNOTATION"):
            stmt = f'''
            SELECT  TRANSITION_ID,
                    ANNOTATION 
                    FROM TRANSITION_PRECURSOR_MAPPING 
                    INNER JOIN TRANSITION ON TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID= TRANSITION.ID
                    WHERE TRANSITION.DETECTING = 1 and PRECURSOR_ID = {precursor_id}
                '''
        else:
            stmt = f'''
            SELECT TRANSITION_ID,
                    TRANSITION.TYPE || TRANSITION.ORDINAL || '^' || TRANSITION.CHARGE AS ANNOTATION
                    FROM TRANSITION_PRECURSOR_MAPPING 
                    INNER JOIN TRANSITION ON TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID = TRANSITION.ID
                    WHERE TRANSITION.DETECTING = 1 and PRECURSOR_ID = {precursor_id}
            '''
        return pd.read_sql(stmt, self.conn)

    def _runIDFromRunName(self, run_name):
        df =  self.runHashTable[self.runHashTable['FILENAME'].str.contains(run_name, regex=False)]['ID']
        if df.empty:
            print(f"Run name {run_name} not found.")
            return None
        else:
            return df.values[0]
        
    def _check_score_ms2(self):
        if self.has_SCORE_MS2:
            return True
        else:
            raise RuntimeError("SCORE_MS2 table not found, please ensure that `pyprophet score` was run on this file")
            return False
    
    def _check_scores_all_levels(self):
        if self.has_SCORE_MS2 and self.has_SCORE_PEPTIDE and self.has_SCORE_PROTEIN:
            return True
        else:
            raise RuntimeError("SCORE_MS2, SCORE_PEPTIDE or SCORE_PROTEIN table not found, please ensure that `pyprophet score`, `pyprophet peptide` and `pyprophet protein` were run on this file")

    #### PUBLIC ACCESSORS ####
    def getAllTopTransitionGroupFeaturesDf(self) -> pd.DataFrame:
        """
        Retrieves all the top ranking features from the database.

        Returns:
            pandas.DataFrame: The top ranking features per assay.
        """
        # Get top ranking feature ids from featureScoreHash
        if 'ms2_mscore' in self.featureScoreHash.columns:
            feature_ids = self.featureScoreHash.loc[self.featureScoreHash["peakgroup_rank"]==1].index.get_level_values("FEATURE_ID")
        else:
            raise KeyError("No ms2_mscore column found in featureScoreHash! You need to perform PyProphet ms2 / ms1ms2 scoring first.")
        
        stmt = f"""SELECT
            PROTEIN.PROTEIN_ACCESSION AS ProteinId,
            PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
            PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
            PRECURSOR.CHARGE AS PrecursorCharge,
            SCORE_MS2.QVALUE AS Qvalue
            from 
            FEATURE
            INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
            INNER JOIN PRECURSOR ON PRECURSOR.ID = FEATURE.PRECURSOR_ID
            INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
            INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
            INNER JOIN PROTEIN ON PROTEIN.ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
            WHERE FEATURE.ID IN ({','.join(map(str, feature_ids))})"""
        data = pd.read_sql(stmt, self.conn)
        
        return data
            
    #### PUBLIC ACCESSORS ####
    def load_data(self) -> pd.DataFrame: ##TODO remove?
        """
        Retrieves all the top ranking features from the database.

        Returns:
            pandas.DataFrame: The top ranking features per assay.
        """
        # Check if EXP_IM in FEATURE table
        if self.has_im: 
            select_feature_exp_im = "FEATURE.EXP_IM AS IM,"
        else:
            select_feature_exp_im = "-1 AS IM,"
        
        # Get top ranking feature ids from featureScoreHash
        if 'ms2_mscore' in self.featureScoreHash.columns:
            feature_ids = self.featureScoreHash.loc[self.featureScoreHash["peakgroup_rank"]==1].index.get_level_values("FEATURE_ID")
        else:
            raise KeyError("No ms2_mscore column found in featureScoreHash! You need to perform PyProphet ms2 / ms1ms2 scoring first.")
            
        stmt = f"""SELECT 
            RUN.FILENAME AS filename,
            FEATURE.EXP_RT AS RT,
            {select_feature_exp_im}
            FEATURE.EXP_RT - FEATURE.DELTA_RT AS assay_rt,
            FEATURE.DELTA_RT AS delta_rt,
            FEATURE.NORM_RT AS iRT,
            PRECURSOR.LIBRARY_RT AS assay_iRT,
            FEATURE.NORM_RT - PRECURSOR.LIBRARY_RT AS delta_iRT,
            PROTEIN.PROTEIN_ACCESSION AS ProteinId,
            PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
            PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
            PRECURSOR.CHARGE AS PrecursorCharge,
            PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
            FEATURE_MS2.AREA_INTENSITY AS Intensity,
            FEATURE_MS1.AREA_INTENSITY AS aggr_prec_Peak_Area,
            FEATURE_MS1.APEX_INTENSITY AS aggr_prec_Peak_Apex,
            FEATURE.LEFT_WIDTH AS leftWidth,
            FEATURE.RIGHT_WIDTH AS rightWidth,
            SCORE_MS2.RANK AS peak_group_rank,
            SCORE_MS2.SCORE AS d_score,
            SCORE_MS2.QVALUE AS Qvalue,
            PRECURSOR.DECOY AS Decoy
        FROM PRECURSOR
        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
        INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
        INNER JOIN PROTEIN ON PROTEIN.ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
        INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
        INNER JOIN RUN ON RUN.ID = FEATURE.RUN_ID
        LEFT JOIN FEATURE_MS1 ON FEATURE_MS1.FEATURE_ID = FEATURE.ID
        LEFT JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
        LEFT JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
        WHERE FEATURE.ID IN ({','.join(map(str, feature_ids))})"""
        data = pd.read_sql(stmt, self.conn)
        
        return data
    
    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel=False):
        """
        Retrives a set of identified precursors

        Args:
            run (str): The run name.
            qvalue (float): The q-value threshold.
            precursorLevel (bool): True indicates q-value filtering only done on the precursor level
        """
        if isinstance(run, str):
            run_id = self._runIDFromRunName(run)
            if precursorLevel and self._check_score_ms2(): #only check q value cutoff on precursor level
                stmt = f"""SELECT DISTINCT
                    PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor
                FROM PRECURSOR
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                WHERE FEATURE.RUN_ID = {run_id} AND SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_MS2.RANK == 1"""
            else:
                if self._check_scores_all_levels():
                    stmt = f"""SELECT DISTINCT
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    INNER JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                    WHERE FEATURE.RUN_ID = {run_id} AND SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_PEPTIDE.QVALUE <= {qvalue} AND SCORE_PROTEIN.QVALUE <= {qvalue} and SCORE_MS2.RANK == 1"""
            rslt = self.conn.execute(stmt)
            return set([i[0] for i in rslt.fetchall()])
        else: # get for all runs
            if precursorLevel: #only check q value cutoff on precursor level
                if self._check_score_ms2():
                    stmt = f"""SELECT 
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE.RUN_ID as RUN_ID
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    WHERE SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_MS2.RANK == 1"""
            else:
                if self._check_scores_all_levels():
                    stmt = f"""SELECT
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE.RUN_ID as RUN_ID
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    INNER JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                    WHERE SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_PEPTIDE.QVALUE <= {qvalue} AND SCORE_PROTEIN.QVALUE <= {qvalue} and SCORE_MS2.RANK == 1"""
            df = pd.read_sql(stmt, self.conn)
            df = df.merge(self.runHashTable, left_on='RUN_ID', right_on='ID')
            return df[['RUN_NAME', 'Precursor']].groupby('RUN_NAME').apply(lambda x: set(x['Precursor'])).to_dict()
    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel=False):
        if isinstance(run, str):
            run_id = self._runIDFromRunName(run)
            if precursorLevel:
                if self._check_score_ms2():
                    stmt = f"""SELECT 
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE_MS2.AREA_INTENSITY AS Intensity
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    INNER JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                    WHERE FEATURE.RUN_ID = {run_id} AND SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_MS2.RANK == 1"""
            else:
                if self._check_scores_all_levels():
                    stmt = f"""SELECT
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE_MS2.AREA_INTENSITY AS Intensity
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    LEFT JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    LEFT JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                    LEFT JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    LEFT JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    LEFT JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                    WHERE FEATURE.RUN_ID = {run_id} AND SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_PEPTIDE.QVALUE <= {qvalue} AND SCORE_PROTEIN.QVALUE <= {qvalue} AND SCORE_MS2.RANK == 1"""
            return pd.read_sql(stmt, self.conn)
        else: # get for all runs
            if precursorLevel:
                if self._check_score_ms2():
                    stmt = f"""SELECT 
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE_MS2.AREA_INTENSITY AS Intensity,
                        FEATURE.RUN_ID as RUN_ID
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    INNER JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                    WHERE SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_MS2.RANK == 1"""
            else:
                if self._check_scores_all_levels():
                    stmt = f"""SELECT
                        PEPTIDE.MODIFIED_SEQUENCE || PRECURSOR.CHARGE  AS Precursor,
                        FEATURE_MS2.AREA_INTENSITY AS Intensity,
                        FEATURE.RUN_ID as RUN_ID
                    FROM PRECURSOR
                    INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
                    INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                    LEFT JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
                    LEFT JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
                    LEFT JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                    LEFT JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    LEFT JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                    WHERE SCORE_MS2.QVALUE <= {qvalue} AND PRECURSOR.DECOY = 0 AND SCORE_PEPTIDE.QVALUE <= {qvalue} AND SCORE_PROTEIN.QVALUE <= {qvalue} AND SCORE_MS2.RANK == 1"""
            df = pd.read_sql(stmt, self.conn)
            df = df.merge(self.runHashTable, left_on='RUN_ID', right_on='ID').drop(columns=['RUN_ID', 'ID', 'FILENAME']).rename(columns={'RUN_NAME': 'runName'})
            return df
  
    def getIdentifiedPeptides(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        if self._check_scores_all_levels():
            if isinstance(run, str):
                run_id = self._runIDFromRunName(run)
                stmt = f"""SELECT
                    PEPTIDE.MODIFIED_SEQUENCE AS Peptide
                    FROM PEPTIDE
                    INNER JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    WHERE SCORE_PEPTIDE.RUN_ID = {run_id} AND SCORE_PEPTIDE.QVALUE <= {qvalue} AND PEPTIDE.DECOY = 0 """
                rslt = self.conn.execute(stmt)
                return set([i[0] for i in rslt.fetchall()])
            else: # get for all runs
                stmt = f"""SELECT
                    PEPTIDE.MODIFIED_SEQUENCE AS Peptide,
                    RUN_ID 
                    FROM PEPTIDE
                    INNER JOIN SCORE_PEPTIDE ON SCORE_PEPTIDE.PEPTIDE_ID = PEPTIDE.ID
                    WHERE SCORE_PEPTIDE.QVALUE <= {qvalue} AND PEPTIDE.DECOY = 0 """
                df = pd.read_sql(stmt, self.conn)
                df = df.merge(self.runHashTable, left_on='RUN_ID', right_on='ID')
                return df[['RUN_NAME', 'Peptide']].groupby('RUN_NAME').apply(lambda x: set(x['Peptide'])).to_dict()
 
    def getIdentifiedProteins(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        if self._check_scores_all_levels():
            if isinstance(run, str):
                run_id = self._runIDFromRunName(run)
                stmt = f"""SELECT
                    PROTEIN.PROTEIN_ACCESSION AS Protein
                    FROM PROTEIN
                    INNER JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PROTEIN.ID
                    WHERE SCORE_PROTEIN.RUN_ID = {run_id} AND SCORE_PROTEIN.QVALUE <= {qvalue} AND PROTEIN.DECOY = 0 """
                rslt = self.conn.execute(stmt)
                return set([i[0] for i in rslt.fetchall()])
            else: # get all runs
                stmt = f"""SELECT
                    PROTEIN.PROTEIN_ACCESSION AS Protein,
                    RUN_ID
                    FROM PROTEIN
                    INNER JOIN SCORE_PROTEIN ON SCORE_PROTEIN.PROTEIN_ID = PROTEIN.ID
                    WHERE SCORE_PROTEIN.QVALUE <= {qvalue} AND PROTEIN.DECOY = 0 """
                df = pd.read_sql(stmt, self.conn)
                df = df.merge(self.runHashTable, left_on='RUN_ID', right_on='ID')
                return df[['RUN_NAME', 'Protein']].groupby('RUN_NAME').apply(lambda x: set(x['Protein'])).to_dict()
   
    def getSoftware(self):
        return "OpenSWATH"

    def getPrecursorIDFromPeptideAndCharge(self, fullpeptidename: str, charge: int) -> int:
        try:
            ## depending on version of pandas this might return a series or number
            # return self.peptideHash.loc[fullpeptidename, charge]['PRECURSOR_ID'].values[0]

            out = self.peptideHash.loc[fullpeptidename, charge]['PRECURSOR_ID']

            if isinstance(out, pd.Series):
                return out.values[0]
            else:
                return out

        except KeyError:
            print(f"Peptide {fullpeptidename} with charge {charge} not found.")
            return None

    def getTransitionGroupFeaturesDf(self, run_basename_wo_ext: str, fullpeptidename: str, charge: int) -> pd.DataFrame:
        run_id = self._runIDFromRunName(run_basename_wo_ext)
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        
        if run_id is None or precursor_id is None:
            features =  pd.DataFrame(columns=self.columns)
        else:
            features =  self._getFeaturesFromPrecursorIdAndRunDf(run_id, precursor_id)

        features['sequence'] = fullpeptidename
        features['precursor_charge'] = charge
        return features[self.columns]

    def getTopTransitionGroupFeatureDf(self, run_basename_wo_ext: str, fullpeptidename: str, charge: int) -> pd.DataFrame:
        columns = self.columns #['filename', 'leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity', 'sequence', 'precursor_charge', 'software']
        run_id = self._runIDFromRunName(run_basename_wo_ext)
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        
        if run_id is None or precursor_id is None:
            features = pd.DataFrame(columns=columns)
        else:
            features = self._getTopFeatureFromPrecursorIdAndRunDf(run_id, precursor_id)

        features['sequence'] = fullpeptidename
        features['precursor_charge'] = charge
        return features[self.columns]

    def getTransitionGroupFeatures(self, run_basename_wo_ext: str, fullpeptidename: str, charge: int) -> List[TransitionGroupFeature]:
        run_id = self._runIDFromRunName(run_basename_wo_ext)
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        
        if run_id is None or precursor_id is None:
            return []
        else:
            return self._getFeaturesFromPrecursorIdAndRun(run_id, precursor_id)

    def getTopTransitionGroupFeature(self, run_basename_wo_ext: str, fullpeptidename: str, charge: int) -> List[TransitionGroupFeature]:
        run_id = self._runIDFromRunName(run_basename_wo_ext)
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        
        if run_id is None or precursor_id is None:
            return None
        else:
            return self._getTopFeatureFromPrecursorIdAndRun(run_id, precursor_id)
    
    def getTransitionIDAnnotationFromSequence(self, fullpeptidename, charge):
        """
        Retrieves transition information for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The transition information.
        """
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        if precursor_id is not None:
            return self._getTransitionsFromPrecursorId(precursor_id)
        else:
            return pd.DataFrame(columns=['TRANSITION_ID', 'ANNOTATION'])
        
    def getRunNames(self) -> List[str]:
        '''
        Infer the run names from the results file, extensions are removed

        Returns:
            list: The run names
        '''
        return self.runHashTable['RUN_NAME'].tolist()

    def _initializeValidScores(self):
        # get valid scores for selection 
        print("Initializing valid scores for selection")
        validScores = {}
        if check_sqlite_table(self.conn, "SCORE_MS2"):
            validScores['SCORE_MS2'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "SCORE_MS1"):
            validScores['SCORE_MS1'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "SCORE_TRANSITION"):
            validScores['SCORE_TRANSITION'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "SCORE_PEPTIDE"):
            validScores['SCORE_PEPTIDE'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "SCORE_PROTEIN"):
            validScores['SCORE_PROTEIN'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "SCORE_IPF"):
            validScores['SCORE_IPF'] = ["SCORE", "PVALUE", "PEP", "QVALUE"]
        if check_sqlite_table(self.conn, "FEATURE_MS2"):
            validScores['FEATURE_MS2'] = []
            stmt = "select * from FEATURE_MS2"
            exec = self.conn.execute(stmt)
            one = exec.fetchone()
            columns = [ d[0] for d in exec.description ]
            for c, v in zip(columns, one):
                if isinstance(v, (int, float)) and c.startswith("VAR"):
                    validScores['FEATURE_MS2'].append(c)
        if check_sqlite_table(self.conn, "FEATURE_MS1"):
            validScores['FEATURE_MS1'] = []
            stmt = "select * from FEATURE_MS1"
            exec = self.conn.execute(stmt)
            one = exec.fetchone()
            columns = [ d[0] for d in exec.description ]
            for c, v in zip(columns, one):
                if isinstance(v, (int, float)) and c.startswith("VAR"):
                    validScores['FEATURE_MS1'].append(c)

        self.validScores = validScores 
    
    def getScoreTable(self, 
                      score_table: Literal['SCORE_MS2', 'SCORE_MS1', 'SCORE_TRANSITION', 'SCORE_PEPTIDE', 'SCORE_PROTEIN', 'SCORE_IPF', 'FEATURE_MS2', 'FEATURE_MS1'], 
                      score: str, # must be in valid scores
                      context: Literal['run-specific', 'experiment-wide', 'global'] = None) -> pd.DataFrame:
        """
        Get a Pandas DataFrame of target and decoy scores for a given score table and score.

        Args:
            score_table Literal["SCORE_MS2", "SCORE_MS1", "SCORE_TRANSITION", "SCORE_PEPTIDE", "SCORE_PROTEIN", "SCORE_IPF", "FEATURE_MS2", "FEATURE_MS1"]] (str): Table which score is found in 
            score (str): The score to retrieve

        Raises:
            ValueError: Score is not valid score for plotting

        Returns:
            pd.DataFrame: A pandas DataFrame with 3 columns: Decoy, Score, and Run Name
        """
        score = score.upper()
        score_table = score_table.upper()
        if score not in self.validScores[score_table]:
            raise ValueError(f"Score {score} in {score_table} table not a valid score for plotting")
        
        if context is None and score_table in ['SCORE_PEPTIDE', 'SCORE_PROTEIN']:
            raise ValueError("Context must be specified for peptide and protein level scores")

        # get the query
        if score_table in ['FEATURE_MS1', 'FEATURE_MS2']:
            stmt = f'''
            SELECT {score_table}.{score} as SCORE,
                DECOY,
                RUN_ID
            FROM {score_table}
            INNER JOIN FEATURE ON {score_table}.FEATURE_ID = FEATURE.ID
            INNER JOIN PRECURSOR ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN SCORE_MS2 ON {score_table}.FEATURE_ID = SCORE_MS2.FEATURE_ID 
            WHERE RANK == 1
            '''
        elif score_table in ['SCORE_MS2']:
            stmt = f'''
            SELECT {score_table}.{score} as SCORE,
            DECOY,
            RUN_ID
            FROM {score_table}
            INNER JOIN FEATURE ON {score_table}.FEATURE_ID = FEATURE.ID
            INNER JOIN PRECURSOR ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
            WHERE RANK == 1
            '''
        elif score_table in ['SCORE_PEPTIDE', 'SCORE_PROTEIN']:
            analyte = score_table.split('_')[1]
            if context in ['run-specific', 'experiment-wide']:
                stmt = f'''
                SELECT {score_table}.{score} as SCORE,
                DECOY,
                RUN_ID
                FROM {score_table}
                INNER JOIN {analyte} ON {score_table}.{analyte}_ID = {analyte}.ID
                WHERE CONTEXT == "{context}" '''
            else: # no run id because global context
                stmt = f'''
                SELECT {score_table}.{score} as SCORE,
                DECOY
                FROM {score_table}
                INNER JOIN {analyte} ON {score_table}.{analyte}_ID = {analyte}.ID
                WHERE CONTEXT == "{context}" '''
        else:
            raise ValueError(f"Score table {score_table} not recognized or not yet implemented")
        
        df = pd.read_sql(stmt, self.conn)
        if context == 'global' and score_table in ['SCORE_PEPTIDE', 'SCORE_PROTEIN']: # no run name for global context
            return df[['DECOY', 'SCORE']]
        else:
            df = df.merge(self.runHashTable, left_on='RUN_ID', right_on='ID')
            return df[['RUN_NAME', 'DECOY', 'SCORE']]


    def get_score_tables(self):
        """
        Retrieves the score tables from the database.

        Returns:
            list: The score tables.
        """
        stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'SCORE%'"
        data = pd.read_sql(stmt, self.conn)

        return data["name"].tolist()
    
    def get_score_table_contexts(self, score_table: str):
        """
        Retrieves the score contexts from the database.

        Returns:
            list: The score contexts.
        """
        stmt = f"SELECT DISTINCT CONTEXT FROM {score_table}"
        data = pd.read_sql(stmt, self.conn)

        return data["CONTEXT"].tolist()

    def get_score_distribution(self, score_table: str, context: Literal['run-specific', 'experiment-wide', 'global'] = None):
        """
        Retrieves the score distribution for a given score table.

        Args:
            score_table (str): The score table.

        Returns:
            pandas.DataFrame: The score distribution.
        """
        if score_table == "SCORE_MS2":
            stmt = '''
            SELECT FEATURE_MS2.*,
                FEATURE.EXP_RT,
                FEATURE.RUN_ID,
                PRECURSOR.VAR_PRECURSOR_CHARGE,
                PRECURSOR.DECOY,
                VAR_TRANSITION_SCORE.VAR_TRANSITION_NUM_SCORE,
                SCORE_MS2.SCORE,
                SCORE_MS2.RANK,
                SCORE_MS2.PVALUE,
                SCORE_MS2.QVALUE,
                SCORE_MS2.PEP,
                RUN_ID || '_' || PRECURSOR_ID AS GROUP_ID
            FROM FEATURE_MS2
            INNER JOIN
            (SELECT RUN_ID,
                    ID,
                    PRECURSOR_ID,
                    EXP_RT
            FROM FEATURE) AS FEATURE ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
            INNER JOIN
            (SELECT ID,
                    CHARGE AS VAR_PRECURSOR_CHARGE,
                    DECOY
            FROM PRECURSOR) AS PRECURSOR ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN
            (SELECT PRECURSOR_ID AS ID,
                    COUNT(*) AS VAR_TRANSITION_NUM_SCORE
            FROM TRANSITION_PRECURSOR_MAPPING
            INNER JOIN TRANSITION ON TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID = TRANSITION.ID
            WHERE DETECTING==1
            GROUP BY PRECURSOR_ID) AS VAR_TRANSITION_SCORE ON FEATURE.PRECURSOR_ID = VAR_TRANSITION_SCORE.ID
            INNER JOIN SCORE_MS2 ON FEATURE.ID = SCORE_MS2.FEATURE_ID
            WHERE RANK == 1
            ORDER BY RUN_ID,
                    PRECURSOR.ID ASC,
                    FEATURE.EXP_RT ASC;
            '''
        elif score_table == "SCORE_MS1":
            stmt = '''
            SELECT FEATURE_MS1*,
                FEATURE.EXP_RT,
                FEATURE.RUN_ID,
                PRECURSOR.VAR_PRECURSOR_CHARGE,
                PRECURSOR.DECOY,
                SCORE_MS1.SCORE,
                SCORE_MS1.RANK,
                SCORE_MS1.PVALUE,
                SCORE_MS1.QVALUE,
                SCORE_MS1.PEP,
                RUN_ID || '_' || PRECURSOR_ID AS GROUP_ID
            FROM FEATURE_MS1
            INNER JOIN
            (SELECT RUN_ID,
                    ID,
                    PRECURSOR_ID,
                    EXP_RT
            FROM FEATURE) AS FEATURE ON FEATURE_MS1.FEATURE_ID = FEATURE.ID
            INNER JOIN
            (SELECT ID,
                    CHARGE AS VAR_PRECURSOR_CHARGE,
                    DECOY
            FROM PRECURSOR) AS PRECURSOR ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN SCORE_MS1 ON FEATURE.ID = SCORE_MS1.FEATURE_ID
            WHERE RANK == 1
            ORDER BY RUN_ID,
                    PRECURSOR.ID ASC,
                    FEATURE.EXP_RT ASC;
            '''
        elif score_table == "SCORE_TRANSITION":
            stmt = '''
            SELECT TRANSITION.DECOY AS DECOY,
                FEATURE_TRANSITION.*,
                PRECURSOR.CHARGE AS VAR_PRECURSOR_CHARGE,
                TRANSITION.VAR_PRODUCT_CHARGE AS VAR_PRODUCT_CHARGE,
                SCORE_TRANSITION.SCORE AS SCORE,
                SCORE_TRANSITION.RANK AS RANK,
                SCORE_TRANSITION.PVALUE AS PVALUE,
                SCORE_TRANSITION.QVALUE AS QVALUE,
                SCORE_TRANSITION.PEP AS PEP,
                RUN_ID || '_' || FEATURE_TRANSITION.FEATURE_ID || '_' || PRECURSOR_ID || '_' || FEATURE_TRANSITION.TRANSITION_ID AS GROUP_ID
            FROM FEATURE_TRANSITION
            INNER JOIN
            (SELECT RUN_ID,
                    ID,
                    PRECURSOR_ID,
                    EXP_RT
            FROM FEATURE) AS FEATURE ON FEATURE_TRANSITION.FEATURE_ID = FEATURE.ID
            INNER JOIN PRECURSOR ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
            INNER JOIN SCORE_TRANSITION ON FEATURE_TRANSITION.FEATURE_ID = SCORE_TRANSITION.FEATURE_ID
            AND FEATURE_TRANSITION.TRANSITION_ID = SCORE_TRANSITION.TRANSITION_ID
            INNER JOIN
            (SELECT ID,
                    CHARGE AS VAR_PRODUCT_CHARGE,
                    DECOY
            FROM TRANSITION) AS TRANSITION ON FEATURE_TRANSITION.TRANSITION_ID = TRANSITION.ID
            ORDER BY RUN_ID,
                    PRECURSOR.ID,
                    FEATURE.EXP_RT,
                    TRANSITION.ID;
            '''
        elif score_table == "SCORE_PEPTIDE":
            stmt = f'''
            SELECT 
                SCORE_PEPTIDE.CONTEXT,
                RUN.FILENAME,
                PEPTIDE.UNMODIFIED_SEQUENCE,
                PEPTIDE.MODIFIED_SEQUENCE,
                PEPTIDE.DECOY,
                SCORE_PEPTIDE.SCORE,
                SCORE_PEPTIDE.PVALUE,
                SCORE_PEPTIDE.QVALUE,
                SCORE_PEPTIDE.PEP
            FROM SCORE_PEPTIDE
            INNER JOIN PEPTIDE ON PEPTIDE.ID = SCORE_PEPTIDE.PEPTIDE_ID
            LEFT JOIN RUN ON RUN.ID = SCORE_PEPTIDE.RUN_ID
            WHERE SCORE_PEPTIDE.CONTEXT = '{context}'
            '''
        elif score_table == "SCORE_IPF":
            stmt = '''
            SELECT 
                PEPTIDE.UNMODIFIED_SEQUENCE,
                PEPTIDE.MODIFIED_SEQUENCE,
                PEPTIDE.DECOY,
                SCORE_IPF.PRECURSOR_PEAKGROUP_PEP,
                SCORE_IPF.QVALUE,
                SCORE_IPF.PEP
            FROM SCORE_IPF
            INNER JOIN PEPTIDE ON PEPTIDE.ID = SCORE_IPF.PEPTIDE_ID
            '''
        elif score_table == "SCORE_PROTEIN":
            stmt = f'''
            SELECT
                SCORE_PROTEIN.CONTEXT,
                RUN.FILENAME,
                PROTEIN.PROTEIN_ACCESSION,
                PROTEIN.DECOY,
                SCORE_PROTEIN.SCORE,
                SCORE_PROTEIN.PVALUE,
                SCORE_PROTEIN.QVALUE,
                SCORE_PROTEIN.PEP
            FROM SCORE_PROTEIN
            INNER JOIN PROTEIN ON PROTEIN.ID = SCORE_PROTEIN.PROTEIN_ID
            LEFT JOIN RUN ON RUN.ID = SCORE_PROTEIN.RUN_ID
            WHERE SCORE_PROTEIN.CONTEXT = '{context}'
            '''
        else:
            raise ValueError(f"Score table {score_table} not supported.")
        
        data = pd.read_sql_query(stmt, self.conn)

        return data

    ##### UNUSED #####
    def get_top_rank_precursor_features_across_runs(self):
        """
        Retrieves the top ranking precursor features across runs from the database.

        Returns:
            pandas.DataFrame: The top ranking precursor features.
        """
        # Get top ranking feature ids from featureScoreHash
        if 'ms2_mscore' in self.featureScoreHash.columns:
            feature_ids = self.featureScoreHash.reset_index().set_index(['FEATURE_ID']).groupby(['PRECURSOR_ID'])[['peakgroup_rank']].idxmin().values.flatten()
        else:
            raise KeyError("No ms2_mscore column found in featureScoreHash! You need to perform PyProphet ms2 / ms1ms2 scoring first.")
        
        stmt = f"""SELECT 
                RUN.FILENAME as filename,
                PROTEIN.PROTEIN_ACCESSION AS ProteinId,
                PEPTIDE.UNMODIFIED_SEQUENCE AS PeptideSequence,
                PEPTIDE.MODIFIED_SEQUENCE AS ModifiedPeptideSequence,
                PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
                PRECURSOR.CHARGE AS PrecursorCharge,
                PRECURSOR.DECOY AS Decoy,
                SCORE_MS2.QVALUE as Qvalue
                FROM FEATURE
                INNER JOIN RUN ON RUN.ID = FEATURE.RUN_ID
                INNER JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
                INNER JOIN PRECURSOR ON PRECURSOR.ID = FEATURE.PRECURSOR_ID
                INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
                INNER JOIN PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
                INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                INNER JOIN PROTEIN ON PROTEIN.ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
                WHERE FEATURE.ID IN ({','.join(map(str, feature_ids))})"""

        data = pd.read_sql(stmt, self.conn)

        return data
    
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

    def get_top_rank_precursor_feature(self, fullpeptidename, charge):
        """
        Retrieves the top ranking precursor feature for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The top ranking precursor feature.
        """
        # Check if fullpeptidename contains a unimod modification at the beginning of the sequence
        if fullpeptidename[0] == "(":
            # If there is a (UniMod:#) at the beginning of the sequence, add a period (.) at the front 
            fullpeptidename = "." + fullpeptidename
        if self.has_im: 
            select_feature_exp_im = "FEATURE.EXP_IM AS IM,"
        else:
            select_feature_exp_im = "-1 AS IM,"
            
        precursor_id = self.getPrecursorIDFromPeptideAndCharge(fullpeptidename, charge)
        
        # Get top ranking feature ids from featureScoreHash
        if 'ms2_mscore' in self.featureScoreHash.columns:
            prec_feature = self.featureScoreHash.loc[(slice(None), precursor_id, slice(None)), :]
            feature_ids = prec_feature.loc[prec_feature["peakgroup_rank"]==1].index.get_level_values("FEATURE_ID")

        else:
            raise KeyError("No ms2_mscore column found in featureScoreHash! You need to perform PyProphet ms2 / ms1ms2 scoring first.")
            
        stmt = f"""SELECT 
            RUN.FILENAME AS filename,
            FEATURE.EXP_RT AS RT,
            {select_feature_exp_im}
            FEATURE.EXP_RT - FEATURE.DELTA_RT AS assay_rt,
            FEATURE.DELTA_RT AS delta_rt,
            FEATURE.NORM_RT AS iRT,
            PRECURSOR.LIBRARY_RT AS assay_iRT,
            FEATURE.NORM_RT - PRECURSOR.LIBRARY_RT AS delta_iRT,
            PROTEIN.PROTEIN_ACCESSION AS ProteinId,
            PEPTIDE.UNMODIFIED_SEQUENCE AS Sequence,
            PEPTIDE.MODIFIED_SEQUENCE AS FullPeptideName,
            PRECURSOR.CHARGE AS PrecursorCharge,
            PRECURSOR.PRECURSOR_MZ AS PrecursorMz,
            FEATURE_MS2.AREA_INTENSITY AS Intensity,
            FEATURE_MS1.AREA_INTENSITY AS aggr_prec_Peak_Area,
            FEATURE_MS1.APEX_INTENSITY AS aggr_prec_Peak_Apex,
            FEATURE.LEFT_WIDTH AS leftWidth,
            FEATURE.RIGHT_WIDTH AS rightWidth,
            SCORE_MS2.RANK AS peak_group_rank,
            SCORE_MS2.SCORE AS d_score,
            SCORE_MS2.QVALUE AS Qvalue,
            PRECURSOR.DECOY AS Decoy
        FROM PRECURSOR
        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR.ID = PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID
        INNER JOIN PEPTIDE ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
        INNER JOIN PROTEIN ON PROTEIN.ID = PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID
        INNER JOIN FEATURE ON FEATURE.PRECURSOR_ID = PRECURSOR.ID
        INNER JOIN RUN ON RUN.ID = FEATURE.RUN_ID
        LEFT JOIN FEATURE_MS1 ON FEATURE_MS1.FEATURE_ID = FEATURE.ID
        LEFT JOIN FEATURE_MS2 ON FEATURE_MS2.FEATURE_ID = FEATURE.ID
        LEFT JOIN SCORE_MS2 ON SCORE_MS2.FEATURE_ID = FEATURE.ID
        WHERE PRECURSOR.ID = {precursor_id} AND FEATURE.ID IN ({','.join(map(str, feature_ids))})"""
        data = pd.read_sql(stmt, self.conn)

        return data
