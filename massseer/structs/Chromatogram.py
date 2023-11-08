import numpy as np
import pyopenms as po
from typing import Optional, Tuple

class Chromatogram:
    ''' 
    This is a single chromatogram object. Holds the data and metadata of a chromatogram
    '''
    def __init__(self, rt, intensity, label = 'None'):
        self.intensity = np.array(intensity)
        self.rt = np.array(rt)
        self.label = label
    def __str__(self):
        return f"{'-'*8} Chromatogram {'-'*8}\nlabel: {self.label}\nlength of chromatogram: {len(self.rt)}"
    
    def to_pyopenms(self, id: Optional[str] = None):
        '''
        Converts the Chromatogram to an OpenMS Chromatogram
        id (str): The nativeID of the chromatogram
        '''
        chrom = po.MSChromatogram()
        chrom.set_peaks((self.rt, self.intensity))
        if id is not None:
            chrom.setNativeID(id)
        return chrom
    
    def max(self, boundary: Optional[Tuple[float,float]] = None) -> float:
        """
        Calculate the highest intensity within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries.

        Returns:
            float: The highest intensity within the given boundary.
        """
        if boundary is not None:
            return self.filterChromatogram(boundary).max()
        else:
            return np.max(self.intensity)
        
    def filterChromatogram(self, boundary: Tuple[float, float]) -> 'Chromatogram':
        """
        Filter the chromatogram to only include data points within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            Chromatogram: A Chromatogram object with filtered retention time and intensity values.
        """
        if isinstance(boundary, tuple):
            left, right = boundary
            mask = (self.rt >= left) & (self.rt <= right)
            return Chromatogram(self.rt[mask], self.intensity[mask], self.label)
        else:
            raise ValueError("Boundary must be a tuple.")   

    def sum(self, boundary: Optional[Tuple[float,float]] = None) -> float:
        """
        Calculates the integrated intensity of a chromatogram within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries of the integration range.

        Returns:
            float: The integrated intensity of the chromatogram within the given boundary.
        """
        if boundary is not None:
            return self.filterChromatogram(boundary).sum()
        else:
            return np.sum(self.intensity)

    def median(self, boundary: Optional[Tuple[float, float]] = None) -> float:
        """
        Calculate the median intensity of a given boundary in the chromatogram data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        """
        if boundary is not None:
            return self.filterChromatogram(boundary).median()
        else:
            return np.median(self.intensity)
