from typing import Tuple
from massseer.structs.Data1D import Data1D
import pandas as pd

class Mobilogram(Data1D):
    ''' 
    This is a single mobilogram object. Holds the data and metadata of a mobilogram
    '''
    def __init__(self, im, intensity, label):
        super().__init__(im, intensity, label)

    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_(self, 'im')