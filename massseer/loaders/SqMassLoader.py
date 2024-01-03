
from abc import ABC, abstractmethod

from pandas.core.api import DataFrame as DataFrame
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.loaders.GenericChromatogramLoader import GenericChromatogramLoader
from massseer.loaders.access.SqMassDataAccess import SqMassDataAccess
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from typing import List, Dict, Union, Literal
from os.path import basename
import pandas as pd

### Plotting
from bokeh.plotting import show
from bokeh.io import output_notebook
from massseer.plotting.InteractivePlotter import InteractivePlotter
from massseer.plotting.GenericPlotter import PlotConfig

class SqMassLoader(GenericChromatogramLoader):

    ''' 
    Class for loading Chromatograms and peak features from SqMass files and OSW files
    Inherits from GenericLoader
    '''

    def __init__(self, rsltsFile: str ,dataFiles: Union[str, List[str]],  verbose: bool = False, mode: Literal['module', 'gui'] = 'module'):
        super().__init__(rsltsFile, dataFiles, 'OpenSWATH', verbose, mode)
        self.dataFiles = [SqMassDataAccess(f) for f in self.dataFiles_str]
        self.rsltsFile = OSWDataAccess(self.rsltsFile_str)

    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        raise NotImplementedError("This function is not implemented for SqMass files")

    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        transitionMetaInfo = self.rsltsFile.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.rsltsFile.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
        columns=['run_name', 'rt', 'intensity', 'annotation']
        if transitionMetaInfo.empty:
            return pd.DataFrame(columns=columns)
        out = {}
        for t in self.dataFiles:

            ### Get Transition chromatogram IDs
            transition_chroms = t.getDataForChromatogramsFromNativeIdsDf(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(precursor_id) 
            precursor_chroms = t.getDataForChromatogramsDf(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            # only add if there is data
            if not transition_chroms.empty or precursor_chroms.empty:
                out[t.filename] = pd.concat([precursor_chroms, transition_chroms])
            elif transition_chroms.empty:
                out[t.filename] = precursor_chroms
            elif precursor_chroms.empty:
                out[t.filename] = transition_chroms
            else:
                print(f"Warning: no data found for peptide in transition file {self.dataFiles}")

        return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='filename'))

    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        transitionMetaInfo = self.rsltsFile.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.rsltsFile.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
 
        if transitionMetaInfo.empty:
            return None
        out = {}
        for t in self.dataFiles:
            ### Get Transition chromatogram IDs

            transition_chroms = t.getDataForChromatogramsFromNativeIds(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(precursor_id)
            precursor_chroms = t.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            out[t] = TransitionGroup(precursor_chroms, transition_chroms)
        return out

    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getTransitionGroupFeaturesDf(runname, pep_id, charge)
            features = features.rename(columns={'ms2_mscore':'qvalue', 'RT':'consensusApex', 'Intensity':'consensusApexIntensity', 'leftWidth':'leftBoundary', 'rightWidth':'rightBoundary'})
            features = features[['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']]
            out[t] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))

    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getTopTransitionGroupFeatureDf(runname, pep_id, charge)
            features = features.rename(columns={'ms2_mscore':'qvalue', 'RT':'consensusApex', 'Intensity':'consensusApexIntensity', 'leftWidth':'leftBoundary', 'rightWidth':'rightBoundary'})
            features = features[['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']]
            out[t] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))


    def plotChromatogram(self,
                        seq: str, 
                        charge: int, 
                        includeBoundaries: bool = True, 
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        scale_intensity: bool = False) -> 'bokeh.plotting.figure.Figure':
        '''
        Plots a chromatogram for a given peptide sequence and charge state for a given run

        Args:
            loader (SqMassLoader): Instance of SqMassLoader
            seq (str): Peptide sequence
            charge (int): Charge state
            includeBoundaries (bool, optional): Whether to include peak boundaries. Defaults to True.
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to False.
            smooth (bool, optional): Whether to smooth the chromatogram. Defaults to True.
            sgolay_polynomial_order (int, optional): Order of the polynomial to use for smoothing. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length to use for smoothing. Defaults to 11.
            scale_intensity (bool, optional): Whether to scale the intensity of the chromatogram such that all chromatograms are individually normalized to 1. Defaults to False.

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''

        ## TODO allow plotting of multiple chromatograms
        if len(self.dataFiles_str) > 1:
            raise NotImplementedError("Only one transition file is supported")
        
        # Initiate Plotting in Jupyter Notebook
        output_notebook()

        # Load the peptide sequence and charge state into the SqlLoader
        # Take the transitions from the first instance of the dictionary returned by the loadTransitionGroupFeature function since there is only run
        transitionGroupFeatures = list(self.loadTransitionGroupFeatures(seq, charge).values())[0]
        transitionGroup = list(self.loadTransitionGroups(seq, charge).values())[0]

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

        show(fig)

        return fig


    def __str__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"
