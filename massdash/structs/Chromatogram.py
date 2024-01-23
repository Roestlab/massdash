"""
massdash/structs/Chromatogram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pyopenms as po
from typing import Optional, Tuple, List
import pandas as pd

# Structs
from .Data1D import Data1D

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
    
    def pad(self, length: int) -> 'Chromatogram':
        """
        Pad the chromatogram with zeros on both sides.

        Args:
            pad (int): The number of zeros to pad on both sides.

        Returns:
            Chromatogram: A new chromatogram object with padded data and intensity.
        """
        new_data, new_intensity = super().pad(length)
        return Chromatogram(new_data, new_intensity, self.label)