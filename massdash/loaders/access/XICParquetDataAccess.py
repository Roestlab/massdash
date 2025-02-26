"""
massdash/loaders/access/XICParquetDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pyarrow.parquet as pq
from pathlib import Path
import pandas as pd
import pyarrow.compute as pc
from typing import Union

# Structs
from ...structs import TransitionGroup, Chromatogram

class XICParquetDataAccess:
    '''
    Class for accessing XIC Parquet files (DIA-NN output)
    '''
    RT_MULTIPLIER = 60
    def __init__(self, filename):
        self.filename = filename
        self.runName = str(Path(filename).stem)
        self.parquet = pq.ParquetFile(filename)
        
        ## Read the index
        self.index = self.parquet.read_row_group(self.parquet.num_row_groups - 2, columns=['pr', 'info']).to_pandas()
        self.index.index = self.index['pr']

    def getTransitionDataDf(self, precursor_id):
        '''
        Get the chromatogram data for a given precursor ID
        '''

        if precursor_id not in self.index.index:
            return pd.DataFrame(columns=['rt', 'value', 'feature'])
        
        out = self._getTransitionDataHelper(precursor_id)

        # Rename columns
        out.rename(columns={'value': 'intensity', 'feature':'annotation'}, inplace=True)
        
        # fix annotation name for MS1
        out.loc[out['annotation'] == 'ms1', 'annotation'] = 'prec'

        out['rt'] = out['rt'] * XICParquetDataAccess.RT_MULTIPLIER

        return out
    
    def getTransitionData(self, pep_id, charge) -> Union[None | TransitionGroup]:
        '''
        Get the chromatogram data for a given precursor ID

        Returns:
            TransitionGroup: TransitionGroup object OR none if pep_id, charge is not found
        '''

        precursor_id = pep_id + str(charge)

        if precursor_id not in self.index.index:
            print(f"Warning: {precursor_id} not found, returning empty TransitionGroup")
            return None
        
        out = self._getTransitionDataHelper(precursor_id)

        # split into transition groups 
        grps = out.groupby('feature')

        transitions = []
        precs = []
        for name, grp in grps:
            if name == 'ms1':
                precs.append(Chromatogram(grp['rt'].values * XICParquetDataAccess.RT_MULTIPLIER, grp['value'].values, 'prec'))
            else:
                transitions.append(Chromatogram(grp['rt'].values * XICParquetDataAccess.RT_MULTIPLIER, grp['value'].values, name))
        
        return TransitionGroup(precs, transitions, pep_id, charge)
    
    def _getTransitionDataHelper(self, precursor_id) -> pd.DataFrame:
        '''
        Get the chromatogram data for a given precursor ID

        Returns:
            pd.DataFrame: Dataframe of chromatogram data
        '''
        ## Get the index of the precursor
        idx = self.index.loc[precursor_id]['info']

        # Read the row group
        out = self.parquet.read_row_group(idx, columns=['rt', 'value', 'feature', 'pr'])

        out = out.filter(pc.equal(out["pr"], precursor_id))
        out = out.drop(['pr'])

        return out.to_pandas()



    




