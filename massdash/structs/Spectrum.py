from typing import Tuple
import pandas as pd

# Structs
from .Data1D import Data1D

class Spectrum(Data1D):
    ''' 
    This is a single spectrum object. Holds the data and metadata of a spectrum
    '''
    def __init__(self, mz, intensity, label):
        super().__init__(mz, intensity, label)
        
    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_(self, 'mz')