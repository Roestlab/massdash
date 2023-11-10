from massseer.plotting.GenericPlotter import GenericPlotter, PlotConfig
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature
from massseer.chromatogram_data_handling import normalize
from typing import List, Optional, Literal

import os
import multiprocessing
import streamlit as st

import numpy as np
from scipy.signal import savgol_filter


import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, Title, Range1d, HoverTool, Label
from bokeh.palettes import Category20, Viridis256

class InteractivePlotter(GenericPlotter):
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        

    def plot(self, transitionGroup: TransitionGroup, features: Optional[List[PeakFeature]] = None, plot_type: Literal['chromatogram', 'mobilogram', 'spectrum'] = 'chromatogram'):
        if plot_type == 'chromatogram':
            return self.plot_chromatogram(transitionGroup)
        elif plot_type == 'mobilogram':
            return self.plot_mobilogram(transitionGroup)
        elif plot_type == 'spectra':
            return self.plot_spectra(transitionGroup)
        else:
            raise ValueError("Unsupported plot plot_type")

    def plot_chromatogram(self, transitionGroup: TransitionGroup):
        # Extract chromatogram data from the transitionGroup
        precursorChroms = transitionGroup.precursorChroms
        transitionChroms = transitionGroup.transitionChroms

        n_transitions = len(transitionChroms)

        # Define a list of distinct colors
        if n_transitions <=20 and n_transitions > 1:
            colors = Category20[len(transitionChroms)]
        elif n_transitions == 1:
            colors = ['black']
        else:
            colors = Viridis256[len(transitionChroms)]

        # Tooltips for interactive information
        TOOLTIPS = [
                ("index", "$index"),
                ("(rt,int)", "(@x{0.00}, @y)"),
                ("precursor_mz", "@precursor_mz"),
                ("product_mz", "@product_mz"),
                ("product_charge", "@product_charge")
            ]

        # Create a Bokeh figure
        p = figure(title=self.title, x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label, width=800, height=400, tooltips=TOOLTIPS)

        # Limit axes ranges
        if self.x_range is not None:
            print(f"Info: Setting x-axis range to: {self.x_range}")
            p.x_range = Range1d(self.x_range[0], self.x_range[1])

        if self.y_range is not None:
            print(f"Info: Setting y-axis range to: {self.y_range}")
            p.y_range = Range1d(self.y_range[0], self.y_range[1])

        p.sizing_mode = 'scale_width'
        # Add a main title
        p.title.text_font_size = "16pt"
        p.title.align = "center"

        # Create a subtitle
        p.add_layout(Title(text=self.subtitle, text_font_style="italic"), 'above')

        # Create a legend
        legend = Legend()

        # Create a list to store legend items
        legend_items = []

        if self.include_ms1:
            # Add precursor chromatograms to the plot
            for i, precursorChrom in enumerate(precursorChroms):
                # Get the retention time and intensity values
                rt = precursorChrom.rt
                intensity = precursorChrom.intensity

                # Smooth the intensity values
                if self.smoothing_dict['type'] == 'sgolay':
                    intensity = savgol_filter(intensity, self.smoothing_dict['sgolay_frame_length'], self.smoothing_dict['sgolay_polynomial_order'])
                elif self.smoothing_dict['type'] == 'none':
                    pass
                else:
                    raise ValueError("Unsupported smoothing type")

                # Scale the intensity values
                if self.scale_intensity:
                    intensity = np.array(normalize(intensity.tolist()))

                # Set negative values in smoothed_intensity to 0
                intensity = np.where(intensity < 0, 0, intensity)

                # Get label for legend
                label = precursorChrom.label

                # Get precursor mz
                precursor_mz = np.unique(transitionGroup.targeted_transition_list['PrecursorMz'].values)[0]

                # Create a ColumnDataSource
                source = ColumnDataSource(data={'x': rt, 'y': intensity, 'precursor_mz': [precursor_mz] * len(rt), 'product_mz': [None] * len(rt), 'product_charge': [None] * len(rt)}
)

                # Plot Precursor trace
                line = p.line('x', 'y', source=source, line_width=2, line_color='black', line_dash="dashed", line_alpha=0.5)

                # Add a legend item
                legend_items.append((label, [line]))

        if self.include_ms2:
            # Add transition chromatograms to the plot
            for i, transitionChrom in enumerate(transitionChroms):
                # Get the retention time and intensity values
                rt = transitionChrom.rt
                intensity = transitionChrom.intensity

                # print(f"rt: {rt}\nint: {intensity}")

                # Smooth the intensity values
                if self.smoothing_dict['type'] == 'sgolay':
                    intensity = savgol_filter(intensity, window_length=self.smoothing_dict['sgolay_frame_length'], polyorder=self.smoothing_dict['sgolay_polynomial_order'])
                elif self.smoothing_dict['type'] == 'none':
                    intensity = intensity
                else:
                    raise ValueError("Unsupported smoothing type")

                # Scale the intensity values
                if self.scale_intensity:
                    intensity = np.array(normalize(intensity.tolist()))

                # Set negative values in smoothed_intensity to 0
                intensity = np.where(intensity < 0, 0, intensity)

                # Get label for legend
                label = transitionChrom.label

                # Get precursor mz
                precursor_mz = transitionGroup.targeted_transition_list['PrecursorMz'].values[0]

                # Get product mz
                # get prdouct_mz from the targeted_transition_list where Annotation = label
                print(label)
                print(transitionGroup.targeted_transition_list)
                print(transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]['ProductMz'])
                product_mz = np.unique(transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]['ProductMz'].values)[0]

                # Get product charge
                product_charge = np.unique(transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]['ProductCharge'].values)[0]

                

                # Create a ColumnDataSource
                source = ColumnDataSource(data={'x': rt, 'y': intensity, 'precursor_mz': [precursor_mz]*len(rt), 'product_mz': [product_mz]*len(rt), 'product_charge': [product_charge]*len(rt)})

                # Plot transition trace
                line = p.line('x', 'y', source=source, line_width=2, line_color=colors[i], line_alpha=0.5)

                # Add a legend item
                legend_items.append((label, [line]))
        
        # Add legend items to the legend
        legend.items = legend_items

        # Add the legend to the plot
        p.add_layout(legend, 'right')

        p.legend.location = "top_left"
        # p.legend.click_policy="hide"
        p.legend.click_policy="mute"

        # Customize the plot
        p.legend.title = "Transition"
        p.legend.label_text_font_size = "10pt"
        p.grid.visible = True

        return p

    def plot_mobilogram(self, transitionGroup: TransitionGroup):
        # Extract mobilogram data from the transitionGroup
        precursorMobilos = transitionGroup.precursorMobilos
        transitionMobilos = transitionGroup.transitionMobilos

        # Create and display mobilogram plots
        # Implement the mobilogram plotting logic here

    def plot_spectra(self, transitionGroup: TransitionGroup):
        # Extract spectra data from the transitionGroup
        precursorSpectra = transitionGroup.precursorSpectra
        transitionSpectra = transitionGroup.transitionSpectra

        # Create and display spectra plots
        # Implement the spectra plotting logic here