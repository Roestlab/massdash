"""
massdash/plotting/SearchResultAnalysisPlots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from typing import Optional, Dict
from itertools import cycle

# Analysis
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

# Bokeh
from bokeh.plotting import figure
from bokeh.layouts import gridplot, column
from bokeh.models import Legend, HoverTool, ColumnDataSource, FactorRange, Whisker, Div
from bokeh.palettes import Category10

# Plotly
import plotly.express as px

# UpSet
import matplotlib.pyplot as plt
import upsetplot

# Internal
from massdash.loaders import ResultsLoader
from massdash.plotting import PlotConfig
from massdash.util import LOGGER

class SearchResultAnalysisPlotConfig(PlotConfig):
    def __init__(self) -> None:
        super().__init__()
        self.aggregate = True # Whether to aggregate runs into one plot or plot as separate 
        self.level = 'precursor' # analyte to plot, can be 'precursor', 'peptide' or 'protein'
        self.statistic_context = 'global' # context for statistics, can be 'global', 'experiment-wide' or 'run-specific'
        self.qvalue = 0.01 # FDR threshold
        self.precursorLevel = False # If True, return the precursor level identification where applicable, else filter identifications on precursor, peptide and protein level


class SearchResultAnalysisPlotter:
    def __init__(self, config: SearchResultAnalysisPlotConfig = SearchResultAnalysisPlotConfig()) -> None:
        self.config = config
        self.fig = None

    def plotIdentifications(self, resultsLoader: ResultsLoader):
        '''
        Plot the identifications

        Args:
            aggregate: (bool) Whether to the runs within a results file
            level: (str) The analyte to plot the plot, can be 'precursor', 'peptide' or 'protein'
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        '''
        if self.config.level == 'precursor':
            counts = resultsLoader.loadNumIdentifiedPrecursors(qvalue=self.config.qvalue)
        elif self.config.level == 'peptide':
            counts = resultsLoader.loadNumIdentifiedPeptides(qvalue=self.config.qvalue, context=self.config.statistic_context)
        elif self.config.level == 'protein':
            counts = resultsLoader.loadNumIdentifiedPrecursors(qvalue=self.config.qvalue, context=self.config.statistic_context)
        else:
            raise Exception(f"Error: Unsupported level {self.config.level}, supported levels are 'precursor', 'peptide' or 'protein'")

        if self.config.aggregate:
            # Get number of rows grouped by column entry and runName

            # get the median and std of identification rates
            median = { s:np.median(list(r.values())) for s, r in counts.items() }
            std = { s:np.std(list(r.values())) for s, r in counts.items() }

            # Create the figure
            p = figure(x_range=FactorRange(*resultsLoader.software),plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "Software"
            p.yaxis.axis_label = "Number of identifications"

            # Create a color cycle for bars
            color_cycle = cycle(Category10[10])

            legend_items = []
            for software in resultsLoader.software:
                std_upper = median[software] + std[software]  # TODO should this /2 
                std_lower = median[software] - std[software] # TODO should this /2 

                # Create a ColumnDataSource from the data
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
            p = figure(x_range=FactorRange(*resultsLoader.runNames), plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "runName"
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
        if self.config.aggregate:
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
         
    def plotQuantifications(self, resultsLoader) -> None:
        '''
        Plot the quantifications
        '''
        quantMatrix = resultsLoader.loadQuantificationMatrix(qvalue=self.config.qvalue).melt(value_name='Intensity')

        # Take the log2 of the Intensity column
        quantMatrix['log2_intensity'] = np.log2(quantMatrix['Intensity'])
        
        p = px.violin(quantMatrix, x="runName", y="log2_intensity", color="Software", box=True, labels = {"runName":'Run', "log2_intensity": "log2(Intensity)"})
        
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
 
    def plotCV(self, resultsLoader) -> None:
        '''
        Plot the CV

        Args:
            **kwargs: Additional arguments to be passed to the getPrecursorIdentifications function
        '''
        # Compute coefficient of variation
        df = resultsLoader.computeCV(qvalue=self.config.qvalue, precursorLevel=self.config.precursorLevel).melt(value_name='CV')

        # Get unique entries and sort them
        
        # Plot violin-boxplot
        p = px.violin(df, x="Software", y="CV", color="Software", box=True, labels = {"CV": "Coefficient of variation (%)"}, category_orders={"Software": resultsLoader.software})

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

    def plotUpset(self, resultsLoader):
        """
        Create an UpSet plot showing the intersection of ModifiedPeptideSequence's between entries
        (with unique ModifiedPeptideSequence across runNames)
        """
        if self.config.level == 'precursor':
            identifications = resultsLoader.loadIdentifiedPrecursors(qvalue=self.config.qvalue, precursorLevel=self.config.precursorLevel)
        elif self.config.level == 'peptide':
            identifications = resultsLoader.loadIdentifiedPeptides(qvalue=self.config.qvalue, context=self.config.statistic_context)
        elif self.config.level == 'protein':
            identifications = resultsLoader.loadIdentifiedProteins(qvalue=self.config.qvalue, context=self.config.statistic_context)
        else:
            raise Exception(f"Error: Unsupported level {self.config.level}, supported levels are 'precursor', 'peptide' or 'protein'")
        
        identifications = self._flattenDict(identifications)

        upset = upsetplot.UpSet(upsetplot.from_contents(identifications))

        fig = plt.figure(figsize=(7, 3))
        upset.plot(fig = fig)
        return fig
    
    def plotPeptideDistribution(self, resultsLoader):
        if not self.config.aggregate and self.config.statistic_context == 'global':
            raise Exception("Error: Global context only supports aggregated plots")
        return self.plotScoreDistribution(resultsLoader, score_table='SCORE_PEPTIDE', score='SCORE', title=f"Peptide Score Distribution ({self.config.statistic_context})")
    
    def plotProteinDistribution(self, resultsLoader):
        if not self.config.aggregate and self.config.statistic_context == 'global':
            raise Exception("Error: Global context only supports aggregated plots")
        return self.plotScoreDistribution(resultsLoader, score_table='SCORE_PROTEIN', score='SCORE', title=f"Protein Score Distribution ({self.config.statistic_context})")
    
    def plotPrecursorDistribution(self, resultsLoader):
        return self.plotScoreDistribution(resultsLoader, score_table='SCORE_MS2', score='SCORE', title="Precursor Score Distribution")

    def _plotScoreDistributionHelper(self, df, score):
        # Create a Bokeh figure
        subtitle = "Aggregated Across Runs" if self.config.aggregate else df['RUN_NAME'].values[0]

        p1 = figure(x_axis_label=score, y_axis_label="# of groups", width=600, height=450) # for histogram
        p2 = figure(x_axis_label=score, y_axis_label="Density", width=600, height=450) # for density plot

        xs = np.linspace(min(df['SCORE']), max(df['SCORE']), 200)

        # Plot histograms for targets
        hist_renderers = []
        dens_renderers = []
        for i in [0, 1]: # 0 is Target, 1 is Decoy
            if not df[df['DECOY'] == i].empty:
                hist, edges = np.histogram(df[df['DECOY'] == i]['SCORE'], bins=20)
                hist_renderers.append(p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], color="blue", alpha=0.7))
                dens_renderers.append(p2.line(xs, gaussian_kde(df[df['DECOY'] == i]['SCORE'])(xs), line_color="blue", line_width=2))
            else:
                LOGGER.warning(f"No {['Target', 'Decoy'][i]} identifications found")

        # Histogram hover tool and legend
        legend_items_hist = [ (i, [r]) for i, r in  list(zip(["Target", "Decoy"], hist_renderers)) ]

        hover1 = HoverTool(renderers=hist_renderers,
                        tooltips=[(f"{score}", "@left"), ("Count", "@top")])
        p1.add_tools(hover1)
        p1.add_layout(Legend(items=legend_items_hist), 'right')
        p1.legend.click_policy="mute"


        # Density hover tool and legend
        legend_items_dens = [ (i, [r]) for i, r in list(zip(["Target", "Decoy"], dens_renderers))]
        hover2 = HoverTool(renderers=dens_renderers,
                        tooltips=[(f"{score}", "@x"), ("Density", "@y")])
        p2.add_tools(hover2)

        p2.add_layout(Legend(items=legend_items_dens), 'right')
        p2.legend.click_policy="mute"
        
        # Create a grid layout
        subtitle_div = Div(text=f"<h2 style='font-style: italic; font-size:11pt; text-align: center;'>{subtitle}</h2>")
        grid = gridplot([p1, p2], ncols=2, sizing_mode="stretch_width")

        return column(subtitle_div, grid)

        # Show the plot

    def plotScoreDistribution(self, resultsLoader: ResultsLoader, score_table: str, score: str, title: Optional[str] =None) -> 'bokeh.layouts.column':
        """
        Plot the score distribution

        Args:
            resultsLoader (ResultsLoader)
            score_table (str): Table to load the score distribution from, must be in validScores
            score (str): Score to load, must be in valid scores
            title (Optional[str], optional): Title of plot. Defaults to None where it will be autoset

        Returns:
            bokeh.layouts.column: Distribution and KDE plot
        """
        title = title if title else f"{score} Distribution"
        df = resultsLoader.loadScoreDistribution(score_table=score_table, score=score, context=self.config.statistic_context)

        if self.config.aggregate:
            title_div = Div(text=f"<h1 style='font-size:13pt; text-align: center;'>{title}</h1>")
            out = self._plotScoreDistributionHelper(df, score)

            return column(title_div, out, sizing_mode="scale_both")

        else:
            plots = []
            for r in df['RUN_NAME'].drop_duplicates().values:
                plots.append(self._plotScoreDistributionHelper(df[df['RUN_NAME'] == r], score))

            title_div = Div(text=f"<h1 style='font-size:13pt; text-align: center;'>{title}</h1>", width=800)
            plots = [title_div] + plots
            return column(plots, sizing_mode='scale_both')
