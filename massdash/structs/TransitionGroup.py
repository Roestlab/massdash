"""
massdash/structs/TransitionGroup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Tuple, Optional, Union, Literal
import pyopenms as po
import pandas as pd

# Structs
from .Chromatogram import Chromatogram
from .Mobilogram import Mobilogram
from .Spectrum import Spectrum
from .TransitionGroupFeature import TransitionGroupFeature

class TransitionGroup:
    '''
    A Transition Group which contains a list of precursor and transition data. Precursor and Transition data must be a Chromatogram, Mobilogram or Spectrum object.
    '''
    def __init__(self, precursorData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]],
                 transitionData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]], sequence: str = None, precursor_charge: int = None):
        """
        Initialize a TransitionGroup object.

        Args:
            precursorData (Union[List[Chromatogram], List[Mobilogram], List[Spectrum]]): _description_
            transitionData (Union[List[Chromatogram], List[Mobilogram], List[Spectrum]]): _description_
            sequence (str, optional): Peptide Sequence. Defaults to None.
            precursor_charge (int, optional): Peptide Charge. Defaults to None.

        Raises:
            ValueError: Precursor and transition data cannot both be empty
        """

        self.precursorData = precursorData
        self.transitionData = transitionData
        if len(transitionData) > 0:
            self.dataType = type(transitionData[0])
        elif len(precursorData) > 0:
            self.dataType = type(precursorData[0])
        else: 
            raise ValueError("Precursor and transition data cannot both be empty")
        if len(precursorData) > 0 and len(transitionData) > 0:
            assert(self.dataType == type(transitionData[0])) 
        self.sequence = sequence
        self.precursor_charge = precursor_charge
  
    def toPandasDf(self, separate=False) -> pd.DataFrame:
        """Convert the TransitionGroup to a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame representation of the TransitionGroup.
        """
        if self.transitionData == [] and self.precursorData == []:
            return pd.DataFrame()
        elif self.transitionData == []:
            return pd.concat([ i.toPandasDf() for i in self.precursorData])
        elif self.precursorData == []:
            return pd.concat([ i.toPandasDf() for i in self.transitionData])
        else:
            transitionDataDf = pd.concat([ i.toPandasDf() for i in self.transitionData])
            precursorDataDf = pd.concat([ i.toPandasDf() for i in self.precursorData])
        
        if separate:
            return precursorDataDf, transitionDataDf
        else:
            return pd.concat([precursorDataDf, transitionDataDf])

    def to_pyopenms(self, includePrecursors=True) -> po.MRMTransitionGroupCP:
        """Convert the TransitionGroup to an OpenMS TransitionGroup.

        Args:
            includePrecursors (bool, optional): If True, include precursor in transition group. Note Precursor and transition chromatograms are not distinguished in this OpenMS representation. Defaults to True.

        Returns:
            po.MRMTransitionGroupCP: An OpenMS TransitionGroup object, can invoke pyopenms methods on this object.
        
        Raises:
            ValueError: Cannot convert Spectrum to pyopenms TransitionGroup
        """
        if self.dataType == Spectrum:
            raise ValueError("Cannot convert Spectrum to pyopenms TransitionGroup")
        transitionGroup = po.MRMTransitionGroupCP()
        for i in range(len(self.transitionData)):
            transition = po.ReactionMonitoringTransition()
            transition.setNativeID(str(i))
            chrom = self.transitionData[i].to_pyopenms(id=str(i))
            transitionGroup.addChromatogram(chrom, chrom.getNativeID())
            transitionGroup.addTransition(transition, transition.getNativeID())

        if includePrecursors:
            for i in range(len(self.precursorData)):
                precursor = po.ReactionMonitoringTransition()
                precursor.setNativeID('p' + str(i))
                chrom = self.precursorData[i].to_pyopenms(id='p' + str(i))
                transitionGroup.addPrecursorChromatogram(chrom, chrom.getNativeID())
        
        return transitionGroup
    
    def max(self, boundary: Tuple[float, float], level: Optional[str] = 'ms1ms2') -> float:
        """
        Calculate the highest intensity within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries.

        Returns:
            float: The highest intensity within the given boundary.
        """
        chroms = self._resolveLevel(level)

        highest_intensity = 0.0  # Initialize with a default value
        for c in chroms:
            intens = c.max(boundary)[1]
            if intens > highest_intensity:
                highest_intensity = intens

        return highest_intensity
    

    def _resolveLevel(self, level):
        if level=='ms1':
            return self.precursorData
        elif level=='ms2':
            return self.transitionData
        elif level=='ms1ms2':
            return self.precursorData + self.transitionData
        else:
            raise ValueError("Level must be one of ['ms1', 'ms2', 'ms1ms2']")

    def sum(self, boundary: Tuple[float, float], level: Optional[Literal['ms1', 'ms2', 'ms1ms2']] = 'ms2') -> float:
        """
        Calculates the integrated intensity of a chromatogram within a given boundary.

        Args:
            boundary (Tuple[float, float]): _description_
            level (Optional[Literal['ms1', 'ms2', 'ms1ms2' ]], optional):The MS level of the data to sum. Defaults to 'ms2'.

        Returns:
            float: The integrated intensity of the chromatogram within the given boundary

        Raises:
            ValueError: Level must be one of ['ms1', 'ms2', 'ms1ms2']

        """
        chroms = self._resolveLevel(level)
        integrated_intensity = 0.0
        for c in chroms:
            integrated_intensity += c.sum(boundary)

        return integrated_intensity
    
    def flatten(self, level: Optional[Literal['ms1', 'ms2', 'ms1ms2']] = 'ms2') -> Union[Chromatogram, Mobilogram, Spectrum]:
        """
        Flatten the TransitionGroup into a single Data1D object.

        Args:
            level (str): The level of the data to sum. Must be one of ['ms1', 'ms2', 'ms1ms2'].

        Returns:
            Union[Chromatogram, Mobilogram, Spectrum]: A single Data1D object containing the flattened data.
        
        Raises:
            ValueError: Level must be one of ['ms1', 'ms2', 'ms1ms2']
        """
        data1D = self._resolveLevel(level)
        data = []
        intensity = []
        for c in data1D:
            data.extend(c.data)
            intensity.extend(c.intensity)
        sorted = pd.DataFrame({'data': data, 'intensity': intensity}).sort_values(by='data')
        return self.dataType(sorted['data'], sorted['intensity'])

    def median(self, boundary: Optional[Tuple[float, float]] = None, level: Optional[str] = 'ms2') -> float:
        """
        Calculate the median intensity of a given boundary in the 1D data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        
        Raises:
            ValueError: Level must be one of ['ms1', 'ms2', 'ms1ms2']
        """

        data_flattened = self.flatten(level)
        if boundary is not None:
            data_flattened = data_flattened.filter(boundary)

        return data_flattened.median()

    def __str__(self) -> str:
        '''
        Returns a string representation of the transition group.

        Returns:
            str: A string representation of the transition group.
        '''
        return f"{'-'*8} TransitionGroup {'-'*8}\nprecursor data: {len(self.precursorData)}\ntransition data: {len(self.transitionData)}\ndata type: {self.dataType.__name__}"

    def empty(self) -> bool:
        """
        Check if the TransitionGroup is empty.

        Returns:
            bool: True if all of the chromatograms, mobilograms, and spectra are empty, False otherwise.
        """
        return not any(p.empty() for p in self.precursorData) and any(t.empty() for t in self.transitionData)
    
    def adjust_length(self, length: int) -> None:
        """
        Adjusts the length size of the chromatograms, mobilograms, and spectra.

        If the length is smaller than the current length, the data will be sliced to the given length.
        If the length is larger than the current length, the data will be padded with zeros on both sides.

        E.g. if the data array is [1, 2, 3] and the desired length is 7, 
        the returned array will be [0, 0, 1, 2, 3, 0, 0].

        E.g. if the data array is [1, 2, 3] and the desired length is 1,
        the returned data array will be [1].

        Args:
            length (int): The length of the output array

        Returns:
            TransitionGroup: A new TransitionGroup object with padded data and intensity.
        """
        new_precursorData = []
        new_transitionData = []
        for c in self.precursorData:
            new_precursorData.append(c.adjust_length(length))
        for c in self.transitionData:
            new_transitionData.append(c.adjust_length(length))
        
        return TransitionGroup(new_precursorData, new_transitionData, self.sequence, self.precursor_charge)
    
    def plot(self, 
             transitionGroupFeatures: Optional[List[TransitionGroupFeature]] = None, 
             smoothing: Optional[Literal['none', 'sgolay', 'gauss']] = 'none',
             gaussian_sigma: float = 2.0,
             gaussian_window: int = 11,
             sgolay_polynomial_order: int = 3,
             sgolay_frame_length: int = 11) -> None:
        """Convenience function for plotting 1D data, meant for jupyter notebook context.

        Args:
            transitionGroupFeatures (Optional[List[TransitionGroupFeature]], optional): list of transition group features include in plot. Defaults to None.
            smoothing (Optional[Literal['none', 'sgolay', 'gauss']], optional): Smoothing to apply on the plot. Defaults to 'none'.
            gaussian_sigma (float, optional): sigma for gaussian plotting, ignored if smoothing is not 'gauss'. Defaults to 2.0.
            gaussian_window (int, optional): window for gaussian plotting, ignored if smoothing is not 'gauss'. Defaults to 11.
            sgolay_polynomial_order (int, optional): Polynomial order for sgolay, ignored if smoothing is not 'sgolay'. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length for sgolay, ignored if smoothing is not 'sgolay'. Defaults to 11.

        Raises:
            ValueError: Unknown type of 1D data
        """
        from ..plotting import PlotConfig
        from ..plotting import InteractivePlotter

        config = PlotConfig()
        if self.dataType == Chromatogram:
            config.plot_type = "chromatogram"
        elif self.dataType == Mobilogram:
            config.plot_type = "mobilogram"
        elif self.dataType == Spectrum:
            config.plot_type = "spectrum"
        else:
            raise ValueError("Unknown type of 1D data")

        config.smoothing_dict = {'type': smoothing, 'sgolay_polynomial_order': sgolay_polynomial_order,
                                 'sgolay_frame_length': sgolay_frame_length,
                                 'gaussian_sigma': gaussian_sigma, 'gaussian_window': gaussian_window}

        plotter = InteractivePlotter(config)

        plotter.plot(self, transitionGroupFeatures, config.plot_type)

        plotter.show()