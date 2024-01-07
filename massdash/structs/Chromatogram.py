import pyopenms as po
from typing import Optional, Tuple, List
import pandas as pd

from massseer.structs.Data1D import Data1D

class Chromatogram(Data1D):
    ''' 
    This is a single chromatogram object. Holds the data and metadata of a chromatogram
    '''
    def __init__(self, rt, intensity, label = 'None'):
        super().__init__(rt, intensity, label)
   
    def to_pyopenms(self, id: Optional[str] = None):
        '''
        Converts the Chromatogram to an OpenMS Chromatogram
        id (str): The nativeID of the chromatogram
        '''
        chrom = po.MSChromatogram()
        chrom.set_peaks((self.data, self.intensity))
        if id is not None:
            chrom.setNativeID(id)
        return chrom
    
    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_('rt')