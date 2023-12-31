from os.path import basename, splitext
from typing import List, Union, Literal, Optional
import numpy as np
import pandas as pd
from bokeh.plotting import show
from bokeh.io import output_notebook
from bokeh.models import Range1d

# Loaders
from massseer.loaders.access.MzMLDataAccess import MzMLDataAccess
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
# Structs
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.FeatureMap import FeatureMap
from massseer.structs.TargetedDIAConfig import TargetedDIAConfig
# Utils
from massseer.util import LOGGER
# Plotting
from massseer.plotting.InteractivePlotter import InteractivePlotter
from massseer.plotting.GenericPlotter import PlotConfig


class MzMLDataLoader(GenericLoader):
    '''
    Class to load data from MzMLFiles using a .osw output file or .tsv report file
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        libraryFile: (str) The path to the library file (.tsv or .pqp)
        
    Methods:
        get_row_indices_for_peptide: Get the row indices in the report for a peptide and charge state
        load_report_for_precursor: Load the report file for a precursor
        load_report: Load the report file
    '''
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], libraryFile: str = None, rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'OpenSWATH', verbose: bool=False, mode: Literal['module', 'gui'] = 'module') -> None:
        super().__init__(rsltsFile, dataFiles, libraryFile, rsltsFileType, verbose, mode)
        self.dataFiles = [MzMLDataAccess(f, 'ondisk', verbose=verbose) for f in self.dataFiles_str]
        self.has_im = np.all([d.has_im for d in self.dataFiles])
                   
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge

        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        out = {}
        for t in self.dataFiles:
            runname = basename(t.filename).split('.')[0]
            out[t.filename] = self.rsltsFile.getTopTransitionGroupFeatureDf(runname, pep_id, charge)
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))
        
    def loadTransitionGroups(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Return:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        out_feature_map = self.loadFeatureMaps(pep_id, charge, config)

        return { run: data.to_chromatograms() for run, data in out_feature_map.items() }

    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig) -> dict[str, FeatureMap]:
        '''
        Loads a dictionary of FeatureMaps (where the keys are the filenames) from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            FeatureMap: FeatureMap object containing peak boundaries, intensity and confidence
        '''
        out = {}
        top_features = [ self.rsltsFile.getTopTransitionGroupFeature(basename(splitext(d.filename)[0]), pep_id, charge) for d in self.dataFiles]
        self.libraryFile.populateTransitionGroupFeatures(top_features)
        for d, t in zip(self.dataFiles, top_features):
            if t is None:
                LOGGER.debug(f"No feature found for {pep_id} {charge} in {d.filename}")
                return FeatureMap()
            else:
                out[d.filename] = d.reduce_spectra(t, config)
        return out

    def plotChromatogram(self,
                        seq: str, 
                        charge: int, 
                        includeBoundaries: bool = True, 
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        scale_intensity: bool = False,
                        mz_tol: float = 20,
                        rt_window: float = 50,
                        im_window: Optional[float] = None) -> 'bokeh.plotting.figure.Figure':
        '''
        Plots a chromatogram for a given peptide sequence and charge state for a given run

        Args:
            seq (str): Peptide sequence
            charge (int): Charge state
            includeBoundaries (bool, optional): Whether to include peak boundaries. Defaults to True.
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to False.
            smooth (bool, optional): Whether to smooth the chromatogram. Defaults to True.
            sgolay_polynomial_order (int, optional): Order of the polynomial to use for smoothing. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length to use for smoothing. Defaults to 11.
            scale_intensity (bool, optional): Whether to scale the intensity of the chromatogram such that all chromatograms are individually normalized to 1. Defaults to False.
            mz_tol (float, optional): m/z tolerance for extraction (in ppm). Defaults to 20.
            rt_tol (float, optional): RT tolerance for extraction (in seconds). Defaults to 50.
            im_tol (float, optional): IM tolerance for extraction (in 1/k0). Defaults to None.

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''

        ## TODO allow plotting of multiple chromatograms
        if len(self.dataFiles_str) > 1:
            raise NotImplementedError("Only one transition file is supported")
        
        # Initiate Plotting in Jupyter Notebook
        output_notebook()

        # specify extraction paramaters
        extraction_parameters = TargetedDIAConfig()
        extraction_parameters.mz_tol = mz_tol
        extraction_parameters.rt_window = rt_window
        extraction_parameters.im_window = im_window

        # Load the peptide sequence and charge state into the SqlLoader
        # Take the transitions from the first instance of the dictionary returned by the loadTransitionGroupFeature function since there is only run
        transitionGroupFeatures = list(self.loadTransitionGroupFeatures(seq, charge).values())[0]
        transitionGroup = list(self.loadTransitionGroups(seq, charge, extraction_parameters).values())[0]

        # Create an instance of the InteractivePlotter class and set appropriate config
        pc = PlotConfig()
        pc.include_ms1 = include_ms1
        if smooth:
            pc.smoothing_dict = {'type': 'sgolay', 'sgolay_polynomial_order': sgolay_polynomial_order, 'sgolay_frame_length': sgolay_frame_length}
        else:
            pc.smoothing_dict = {'type': 'none'}
        pc.scale_intensity = scale_intensity

        plotter = InteractivePlotter(pc)

        # Plot the chromatogram data
        fig = plotter.plot(transitionGroup)

        # Add boundaries to the plot
        if includeBoundaries:
            fig = plotter.add_peak_boundaries(fig, transitionGroupFeatures)

        centerApex = list(self.loadTopTransitionGroupFeature(seq, charge).values())[0].consensusApex
        fig.x_range = Range1d(*extraction_parameters.get_rt_upper_lower(centerApex))
        show(fig)

        return fig

