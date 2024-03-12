"""
massdash/loaders/ResultsLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
from os.path import basename
from typing import Dict, List, Union, Literal, Optional
import pandas as pd
from pathlib import Path 
import numpy as np

# Loaders
from .SpectralLibraryLoader import SpectralLibraryLoader
from .access.OSWDataAccess import OSWDataAccess
from .access.ResultsTSVDataAccess import ResultsTSVDataAccess
# Structs
from ..structs import TransitionGroup, TransitionGroupFeatureCollection, TopTransitionGroupFeatureCollection
# Utils
from ..util import LOGGER
# Plotting
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange, Whisker, Legend, HoverTool
from bokeh.palettes import Category10
from bokeh.layouts import gridplot
from itertools import cycle
import plotly.express as px

class ResultsLoader:
    ''' 
    Class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, 
                 rsltsFile: Union[str, List[str]], 
                 libraryFile: str = None,
                 verbose: bool=False, 
                 mode: Literal['module', 'gui'] = 'module'):

        # Attributes (set further down)
        self.rsltsAccess = []
        self.libraryAccess = None
        self.runNames = None
        self.verbose = verbose
        self.libraryFile = libraryFile
        self.software = None

        if isinstance(rsltsFile, str):
            self.rsltsFile = [rsltsFile]
        else:
            self.rsltsFile = rsltsFile

        LOGGER.name = __class__.__name__
        if self.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

        # Make rsltsFile iterable if it is not already
        ### set the results file depending on the file ending
        for f in self.rsltsFile:
            if f.endswith('.osw'):
                self.rsltsAccess.append(OSWDataAccess(f, verbose=verbose, mode=mode))
            elif f.endswith('.tsv'):
                self.rsltsAccess.append(ResultsTSVDataAccess(f, verbose=verbose))
            else:
                raise Exception(f"Error: Unsupported file type {f} or unsupported rsltsFileType {f}")
              
        # If called as a Results loader, infer the run names since no raw data will be used.
        self.runNames = self._inferRunNames()
        self.software = self._loadSoftware()

        if self.libraryFile is not None:
            self.libraryAccess = SpectralLibraryLoader(self.libraryFile)
            self.libraryAccess.load()


    def _inferRunNames(self):
        '''
        Infer the run names from the results file
        '''
        runNames = set()
        for f in self.rsltsAccess:
            runNames = runNames.union(set(f.getRunNames()))
        return list(runNames)
    
    def _loadSoftware(self):
        '''
        Load the software used for identification
        '''
        return [i.getSoftware() for i in self.rsltsAccess]

    @abstractmethod
    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge

        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        pass

    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        
        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs
        '''
        out = {}
        for d in self.runNames:
            for r in self.rsltsAccess:
                features = r.getTransitionGroupFeaturesDf(d, pep_id, charge)
                out[d] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='runname'))

    def loadTransitionGroupFeatures(self, pep_id: str, charge: int) -> TransitionGroupFeatureCollection:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            PeakFeature: PeakFeature object containing peak boundaries, intensity and confidence
        '''
        out = TransitionGroupFeatureCollection()
        for t in self.runNames:
            runname = basename(t).split('.')[0]
            feats = []
            for r in self.rsltsAccess:
                feats += r.getTransitionGroupFeatures(runname, pep_id, charge)
            out[t] = feats
        return out
    
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
        for d in self.runNames:
            for r in self.rsltsAccess:
                features = r.getTopTransitionGroupFeatureDf(d, pep_id, charge)
                out[d] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))

    def loadTopTransitionGroupFeature(self, pep_id: str, charge: int) -> TransitionGroupFeatureCollection:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            TransitionGroup: TransitionGroup object containing peak boundaries, intensity and confidence
        '''
        out = TransitionGroupFeatureCollection()
        for t in self.runNames:
            runname = basename(t).split('.')[0]
            feats = []
            for r in self.rsltsAccess:
                feats.append(r.getTopTransitionGroupFeature(runname, pep_id, charge))
            out[t] = feats
        return out
    
    def loadIdentifiedPrecursors(self, **kwargs):
        '''
        Load the precursor identifications

        **kwargs: Additional arguments to be passed to the getIdentifiedPrecursors function
        '''
        return {i.getSoftware():i.getIdentifiedPrecursors(**kwargs) for i in self.rsltsAccess}
    
    def loadNumIdentifiedPrecursors(self, **kwargs):
        '''
        Load the number of precursor identifications

        **kwargs: Additional arguments to be passed to the getIdentifiedPrecursors function
        '''
        return {i.getSoftware():i.getNumIdentifiedPrecursors(**kwargs) for i in self.rsltsAccess}

    def loadIdentifiedProteins(self, **kwargs):
        '''
        Load the protein identifications

        **kwargs: Additional arguments to be passed to the getIdentifiedProteins function
        '''
        return {i.getSoftware():i.getIdentifiedProteins(**kwargs) for i in self.rsltsAccess}
    
    def loadNumIdentifiedProteins(self, **kwargs):
        '''
        Load the number of protein identifications

        Args:
            **kwargs: Additional arguments to be passed to the getIdentifiedProteins function
        '''
        return {i.getSoftware():i.getNumIdentifiedProteins(**kwargs) for i in self.rsltsAccess}

    def loadIdentifiedPeptides(self, **kwargs):
        '''
        Load the peptide identifications

        **kwargs: Additional arguments to be passed to the getIdentifiedPeptides function
        '''
        return {i.getSoftware():i.getIdentifiedPeptides(**kwargs) for i in self.rsltsAccess}
    
    def loadNumIdentifiedPeptides(self, **kwargs):
        '''
        Load the number of peptide identifications

        Args:
            **kwargs: Additional arguments to be passed to the getIdentifiedPeptides function
        '''
        return {i.getSoftware():i.getNumIdentifiedPeptides(**kwargs) for i in self.rsltsAccess}
    
    
    def loadExperimentSummary(self) -> pd.DataFrame:
        '''
        load a pandas dataframe summary of the experiment for all result files
        '''
        return pd.concat([i.getExperimentSummary().T for i in self.rsltsAccess]).sort_index().T

    def loadNumPeptideIdentifications(self, **kwargs) -> pd.DataFrame:
        '''
        Load the number of peptide identifications

        **kwargs: Additional arguments to be passed to the getNumPeptideIdentifications function
        '''
        return {i.getSoftware():i.getNumPeptideIdentifications(**kwargs) for i in self.rsltsAccess}
   
    def loadQuantificationMatrix(self, **kwargs) -> pd.DataFrame:
        '''
        load a quantification matrix

        Args:
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        
        Returns:
            DataFrame: DataFrame containing the quantification matrix, columns are the software tool, index are the precursor and the values are the intensities
        '''
        tmp =  pd.concat({ i.getSoftware():i.getIdentifiedPrecursorIntensities(**kwargs) for i in self.rsltsAccess }).drop_duplicates()
        return (tmp
                .drop_duplicates()
                .reset_index()
                .rename(columns={'level_0':'Software'})
                .pivot(index='Precursor', columns=['Software', 'filename'], values='Intensity'))

    def computeCV(self, **kwargs) -> pd.DataFrame:
        '''
        Compute the CV (coefficient of variation) of the identified precursors

        Args:
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        
        Returns:
            DataFrame: DataFrame containing the CV of the identified precursors, columns are the software tool, index are the precursor and the values are the CV
        '''
        tmp = pd.concat({i.getSoftware():i.getPrecursorCVs(**kwargs) for i in self.rsltsAccess})
        return (tmp
                .drop_duplicates()
                .reset_index()
                .rename(columns={'level_0':'Software'})
                .pivot(index='Precursor', columns=['Software'], values='CV'))

    def plotIdentifications(self, aggregate, level: Literal['precursor', 'peptide', 'protein'], **kwargs) -> None:
        '''
        Plot the identifications

        Args:
            aggregate: (str) The level of aggregation for the plot, can be 'precursor', 'peptide' or 'protein'
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        '''
        if level == 'precursor':
            counts = self.loadNumIdentifiedPrecursors(**kwargs)
        elif level == 'peptide':
            counts = self.loadNumIdentifiedPeptides(**kwargs)
        elif level == 'protein':
            counts = self.loadNumIdentifiedPrecursors(**kwargs)
        else:
            raise Exception(f"Error: Unsupported level {level}, supported levels are 'precursor', 'peptide' or 'protein'")

        if aggregate:
            # Get number of rows grouped by column entry and filename

            # get the median and std of identification rates
            median = { s:np.median(list(r.values())) for s, r in counts.items() }
            std = { s:np.std(list(r.values())) for s, r in counts.items() }

            # Create the figure
            p = figure(x_range=FactorRange(*self.software),plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "Software"
            p.yaxis.axis_label = "Number of identifications"

            # Create a color cycle for bars
            color_cycle = cycle(Category10[10])

            legend_items = []
            for software in self.software:
                std_upper = median[software] + std[software]  # TODO should this /2 
                std_lower = median[software] - std[software] # TODO should this /2 

                # Create a ColumnDataSource from the data
                print(median[software])
                source = ColumnDataSource(data=dict(x=[software], y=[median[software]], upper=[std_upper], lower=[std_lower]))

                # Get the next color from the cycle
                color = next(color_cycle)

                # Add the bar glyphs with unique color
                bar = p.vbar(x="x", top="y", width=0.9, source=source, color=color)

                # Add the error bars (standard deviation)
                whisker = Whisker(source=source, base="x", upper="upper", lower="lower", line_color="black", line_width=1.5, level="annotation")
                p.add_layout(whisker)

                # Add the legend item
                legend_items.append((software, [bar]))
                
            # Set y-axis to max upper std value + padding of 50
            p.y_range.end = std_upper * 1.2
        else:

            #TODO this is currently broken bars ontop of one another
            # Create the figure
            p = figure(x_range=FactorRange(*self.runNames), plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "Filename"
            p.yaxis.axis_label = "Number of identifications"

            # Create a color cycle for bars
            color_cycle = cycle(Category10[10])

            legend_items = []
            for software, exp in counts.items():
                for run, counts in exp.items():
                    # Create a ColumnDataSource from the data
                    print(counts)
                    print(run)
                    source = ColumnDataSource(data=dict(x=[run], y=[counts]))

                    # Get the next color from the cycle
                    color = next(color_cycle)

                    # Add the bar glyphs with unique color
                    bar = p.vbar(x="x", top="y", width=0.9, source=source, color=color)

                    # Add the legend item
                    legend_items.append((run, [bar]))

        legend = Legend(items=legend_items, location="center_right")
        p.add_layout(legend, 'right')
        
        # Enable click-to-hide for the legend
        p.legend.click_policy = "hide"
        # Legend text size
        p.legend.label_text_font_size = "15pt"

        # Add a hover tool
        hover = HoverTool()
        if aggregate:
            hover.tooltips = [("Entry", "@x"), ("Median Count", "@y{int}"), ("Upper Std", "@upper{int}"), ("Lower Std", "@lower{int}")]
        else:
            hover.tooltips = [("Sample", "@x"), ("Count", "@y")]
        p.add_tools(hover)

        # Customize plot attributes
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        
        # Make labels and axis text larger
        p.xaxis.axis_label_text_font_size = "18pt"
        p.yaxis.axis_label_text_font_size = "18pt"
        p.xaxis.major_label_text_font_size = "16pt"
        p.yaxis.major_label_text_font_size = "16pt"
        
        return p
         
    def plotQuantifications(self, **kwargs) -> None:
        '''
        Plot the quantifications
        '''
        quantMatrix = self.loadQuantificationMatrix(**kwargs).melt(value_name='Intensity')
        print(quantMatrix['Software'])

        # Take the log2 of the Intensity column
        quantMatrix['log2_intensity'] = np.log2(quantMatrix['Intensity'])
        
        p = px.violin(quantMatrix, x="filename", y="log2_intensity", color="Software", box=True, labels = {"filename":'Run', "log2_intensity": "log2(Intensity)"})
        
        # Update label and axis text size
        p.update_layout(
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            xaxis_tickfont_size=16,
            yaxis_tickfont_size=16,
            legend_title_font_size=18,
            legend_font_size=16,
        )
        
        p.update_xaxes(type='category')
        return p
 
    def plotCV(self, **kwargs) -> None:
        '''
        Plot the CV

        Args:
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        '''
        # Compute coefficient of variation
        df = self.computeCV(**kwargs).melt(value_name='CV')

        # Get unique entries and sort them
        
        # Plot violin-boxplot
        p = px.violin(df, x="Software", y="CV", color="Software", box=True, labels = {"CV": "Coefficient of variation (%)"}, category_orders={"Software": self.software})

        # Update label and axis text size
        p.update_layout(
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            xaxis_tickfont_size=16,
            yaxis_tickfont_size=16,
            legend_title_font_size=18,
            legend_font_size=16,
        )
        
        p.update_xaxes(type='category')
        return p
    
    @staticmethod
    def _flattenDict(d: Dict[str, Dict[str, set]]) -> Dict[str,set]:
        '''
        Flatten a dictionary of dictionaries
        Helper for plotUpset
        '''
        out = {}
        for k1,v1 in d.items():
            for k2,v2 in v1.items():
                out[f'{k2} ({k1})'] = v2
        return out

    def plotUpset(self, level= Literal['precursor', 'peptide', 'protein'], **kwargs):
        """
        Create an UpSet plot showing the intersection of ModifiedPeptideSequence's between entries
        (with unique ModifiedPeptideSequence across filenames)
        """
        import upsetplot
        import matplotlib.pyplot as plt
        from io import BytesIO

        if level == 'precursor':
            identifications = self.loadIdentifiedPrecursors(**kwargs)
        elif level == 'peptide':
            identifications = self.loadIdentifiedPeptides(**kwargs)
        elif level == 'protein':
            identifications = self.loadIdentifiedProteins(**kwargs)
        else:
            raise Exception(f"Error: Unsupported level {level}, supported levels are 'precursor', 'peptide' or 'protein'")
        
        identifications = self._flattenDict(identifications)

        upset = upsetplot.UpSet(upsetplot.from_contents(identifications))

        fig = plt.figure(figsize=(7, 3))
        return upset.plot(fig = fig)
  
    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile}"
