"""
massdash/structs/TransitionGroupCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pandas as pd
import numpy as np

# Internal Imports
from .GenericStructCollection import GenericStructCollection

class TransitionGroupCollection(GenericStructCollection):
    '''
    A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroup>
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def toPandasDf(self) -> pd.DataFrame:
        '''
        Convert the TransitionGroupCollection to a pandas DataFrame
        '''
        tmp =  pd.concat([v.toPandasDf() for v in self.values()], keys=self.keys(), axis=0)
        tmp['run'] = tmp.index.get_level_values(0)
        tmp = tmp.reset_index(drop=True)
        return tmp