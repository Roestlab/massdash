import streamlit as st
import numpy as np
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.models import Line, ColumnDataSource, Legend, Title, Range1d, HoverTool, Label
from bokeh.palettes import Category20, Viridis256

from massseer.plotting.GenericPlotter import GenericPlotter, PlotConfig
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature
from massseer.structs.Chromatogram import Chromatogram
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
from massseer.chromatogram_data_handling import normalize
from massseer.util import check_streamlit
from typing import List, Optional, Literal



class InteractivePlotter(GenericPlotter):
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)

    def plot(self, transitionGroup: TransitionGroup, features: Optional[List[PeakFeature]] = None, plot_type: Literal['chromatogram', 'mobilogram', 'spectrum'] = 'chromatogram') -> figure:
        """
        Plots the given transitionGroup using the specified plot type.

        Args:
            transitionGroup (TransitionGroup): The transition group to plot.
            features (Optional[List[PeakFeature]], optional): A list of peak features to highlight on the plot. Defaults to None.
            plot_type (Literal['chromatogram', 'mobilogram', 'spectrum'], optional): The type of plot to generate. Defaults to 'chromatogram'.

        Returns:
            figure: The generated plot as a Bokeh figure object.
        """
        if plot_type == 'chromatogram':
            return self.plot_chromatogram(transitionGroup)
        elif plot_type == 'mobilogram':
            return self.plot_mobilogram(transitionGroup)
        elif plot_type == 'spectra':
            return self.plot_spectra(transitionGroup)
        else:
            raise ValueError("Unsupported plot plot_type")

    def process_chrom(self, p: figure, chrom: Chromatogram, label: str, color: str='black', line_type: str="dashed", is_precursor: bool=True, transitionGroup: TransitionGroup=None) -> Line:
            """
            Process a chromatogram and add it to a Bokeh figure.

            Args:
                p (figure): Bokeh figure to add the chromatogram to.
                chrom (Chromatogram): Chromatogram object to process.
                label (str): Label for the chromatogram.
                color (str, optional): Color for the chromatogram line. Defaults to 'black'.
                line_type (str, optional): Line type for the chromatogram line. Defaults to "dashed".
                is_precursor (bool, optional): Whether the chromatogram is for the precursor ion. Defaults to True.
                transitionGroup (TransitionGroup, optional): TransitionGroup object containing precursor and product ion information. Defaults to None.

            Returns:
                Line: Bokeh line object representing the chromatogram.
            """
            rt = chrom.rt
            intensity = chrom.intensity

            if self.smoothing_dict['type'] == 'sgolay':
                try:
                    intensity = savgol_filter(intensity, window_length=self.smoothing_dict['sgolay_frame_length'], polyorder=self.smoothing_dict['sgolay_polynomial_order'])
                except ValueError as ve:
                    if 'window_length must be less than or equal to the size of x' in str(ve):
                        error_message = f"Error: The specified window length for sgolay smoothing is too large for transition = {label}. Try adjusting it to a smaller value."
                    else:
                        error_message = f"Error: {ve}"

                    if check_streamlit():
                        st.error(error_message)
                    else:
                        raise ValueError(error_message)
            elif self.smoothing_dict['type'] == 'none':
                pass
            else:
                raise ValueError("Unsupported smoothing type")

            if self.scale_intensity:
                intensity = np.array(normalize(intensity.tolist()))

            intensity = np.where(intensity < 0, 0, intensity)

            # Get precursor and product info
            precursor_mz = transitionGroup.targeted_transition_list['PrecursorMz'].values[0]
            product_mz = None
            product_charge = None

            if not is_precursor:
                label_info = transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]
                product_mz = np.unique(label_info['ProductMz'].values)[0]
                product_charge = np.unique(label_info['ProductCharge'].values)[0]

            source_data = {'x': rt, 'y': intensity, 'precursor_mz': [precursor_mz] * len(rt),
                        'product_mz': [product_mz] * len(rt), 'product_charge': [product_charge] * len(rt)}

            source = ColumnDataSource(data=source_data)
            line = p.line('x', 'y', source=source, line_width=2, line_color=color, line_alpha=0.5, line_dash=line_type)

            return line

    def plot_chromatogram(self, transitionGroup: TransitionGroup) -> figure:
            """
            Plots a chromatogram for a given TransitionGroup.

            Args:
                transitionGroup (TransitionGroup): The TransitionGroup to plot.

            Returns:
                A Bokeh figure object representing the chromatogram plot.
            """
            # Extract chromatogram data from the transitionGroup
            precursorChroms = transitionGroup.precursorChroms
            transitionChroms = transitionGroup.transitionChroms

            n_transitions = len(transitionChroms)

            # Define a list of distinct colors
            if n_transitions <=20 and n_transitions > 2:
                colors = Category20[len(transitionChroms)]
            elif n_transitions <=2 and n_transitions > 0:
                colors = Category20[3]
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
                for precursorChrom in precursorChroms:
                    label = precursorChrom.label
                    line = self.process_chrom(p, precursorChrom, label, transitionGroup=transitionGroup)
                    legend_items.append((label, [line]))

            if self.include_ms2:
                for i, transitionChrom in enumerate(transitionChroms):
                    label = transitionChrom.label
                    line = self.process_chrom(p, transitionChrom, label, color=colors[i], line_type='solid', is_precursor=False, transitionGroup=transitionGroup)
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

    def process_mobilo(self, p: figure, mobilo: Mobilogram, label: str, color: str='black', line_type: str="dashed", is_precursor: bool=True, transitionGroup: TransitionGroup=None) -> Line:
        """
        Process a mobilogram and add it to a Bokeh figure.

        Args:
            p (figure): Bokeh figure to add the mobilogram to.
            mobilo (Mobilogram): Mobilogram object to process.
            label (str): Label for the mobilogram.
            color (str, optional): Color for the mobilogram line. Defaults to 'black'.
            line_type (str, optional): Line type for the mobilogram line. Defaults to "dashed".
            is_precursor (bool, optional): Whether the mobilogram is for the precursor ion. Defaults to True.
            transitionGroup (TransitionGroup, optional): TransitionGroup object containing precursor and product ion information. Defaults to None.

        Returns:
            Line: Bokeh line object representing the mobilogram.
        """
        im = mobilo.im
        intensity = mobilo.intensity

        if self.smoothing_dict['type'] == 'sgolay':
            try:
                intensity = savgol_filter(intensity, window_length=self.smoothing_dict['sgolay_frame_length'], polyorder=self.smoothing_dict['sgolay_polynomial_order'])
            except ValueError as ve:
                if 'window_length must be less than or equal to the size of x' in str(ve):
                    error_message = f"Error: The specified window length for sgolay smoothing is too large for transition = {label}. Try adjusting it to a smaller value."
                else:
                    error_message = f"Error: {ve}"

                if check_streamlit():
                    st.error(error_message)
                else:
                    raise ValueError(error_message)
        elif self.smoothing_dict['type'] == 'none':
            pass
        else:
            raise ValueError("Unsupported smoothing type")

        if self.scale_intensity:
            intensity = np.array(normalize(intensity.tolist()))

        intensity = np.where(intensity < 0, 0, intensity)

        # Get precursor and product info
        precursor_mz = transitionGroup.targeted_transition_list['PrecursorMz'].values[0]
        product_mz = None
        product_charge = None

        if not is_precursor:
            label_info = transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]
            product_mz = np.unique(label_info['ProductMz'].values)[0]
            product_charge = np.unique(label_info['ProductCharge'].values)[0]

        source_data = {'x': im, 'y': intensity, 'precursor_mz': [precursor_mz] * len(im), 'product_mz': [product_mz] * len(im), 'product_charge': [product_charge] * len(im)}

        source = ColumnDataSource(data=source_data)
        line = p.line('x', 'y', source=source, line_width=2, line_color=color, line_alpha=0.5, line_dash=line_type)

        return line

    def plot_mobilogram(self, transitionGroup: TransitionGroup) -> figure:
        """
        Plots the mobilogram for a given TransitionGroup.

        Args:
            transitionGroup (TransitionGroup): The TransitionGroup to plot the mobilogram for.

        Returns:
            figure: The matplotlib figure object containing the mobilogram plot.
        """
        # Extract mobilogram data from the transitionGroup
        precursorMobilos = transitionGroup.precursorMobilos
        transitionMobilos = transitionGroup.transitionMobilos

        n_transitions = len(transitionMobilos)

        # Define a list of distinct colors
        if n_transitions <=20 and n_transitions > 2:
            colors = Category20[len(transitionMobilos)]
        elif n_transitions <=2 and n_transitions > 0:
            colors = Category20[3]
        elif n_transitions == 1:
            colors = ['black']
        else:
            colors = Viridis256[len(transitionMobilos)]

        # Tooltips for interactive information
        TOOLTIPS = [
                ("index", "$index"),
                ("(im,int)", "(@x{0.00}, @y)"),
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
            for precursorMobilo in precursorMobilos:
                label = precursorMobilo.label
                line = self.process_mobilo(p, precursorMobilo, label, transitionGroup=transitionGroup)
                legend_items.append((label, [line]))

        if self.include_ms2:
            for i, transitionMobilo in enumerate(transitionMobilos):
                label = transitionMobilo.label
                line = self.process_mobilo(p, transitionMobilo, label, color=colors[i], line_type='solid', is_precursor=False, transitionGroup=transitionGroup)
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

    def process_spectra(self, p: figure, spectra: Spectrum, label: str, color: str='black', line_type: str="dashed", is_precursor: bool=True, transitionGroup: TransitionGroup=None) -> Line:
        """
        Process a spectrum and add it to a Bokeh figure.

        Args:
            p (figure): Bokeh figure to add the spectrum to.
            spectra (Spectrum): Spectrum object to process.
            label (str): Label for the spectrum.
            color (str, optional): Color for the spectrum line. Defaults to 'black'.
            line_type (str, optional): Line type for the spectrum line. Defaults to "dashed".
            is_precursor (bool, optional): Whether the spectrum is for the precursor ion. Defaults to True.
            transitionGroup (TransitionGroup, optional): TransitionGroup object containing precursor and product ion information. Defaults to None.

        Returns:
            Line: Bokeh line object representing the spectrum.
        """
        mz = spectra.mz
        intensity = spectra.intensity

        if self.scale_intensity:
            intensity = np.array(normalize(intensity.tolist()))

        intensity = np.where(intensity < 0, 0, intensity)

        # Get precursor and product info
        precursor_mz = transitionGroup.targeted_transition_list['PrecursorMz'].values[0]
        product_mz = None
        product_charge = None

        if not is_precursor:
            label_info = transitionGroup.targeted_transition_list[transitionGroup.targeted_transition_list['Annotation'] == label]
            product_mz = np.unique(label_info['ProductMz'].values)[0]
            product_charge = np.unique(label_info['ProductCharge'].values)[0]

        source_data = {'x': mz, 'y0':[0]*len(mz), 'y': intensity, 'precursor_mz': [precursor_mz] * len(mz), 'product_mz': [product_mz] * len(mz), 'product_charge': [product_charge] * len(mz)}

        source = ColumnDataSource(data=source_data)
        line = p.vbar('x', bottom='y0', top='y', source=source, width=0.1, line_width=2, line_color=color, line_alpha=0.5, line_dash=line_type)

        return line
    

    def plot_spectra(self, transitionGroup: TransitionGroup) -> figure:
        """
        Plots the spectra data for a given transition group.

        Parameters:
        -----------
        transitionGroup : TransitionGroup
            The transition group for which to plot the spectra data.

        Returns:
        --------
        figure : bokeh.plotting.figure
            The Bokeh figure object containing the plotted spectra data.
        """
        # Extract spectra data from the transitionGroup
        precursorSpectra = transitionGroup.precursorSpectra
        transitionSpectra = transitionGroup.transitionSpectra

        n_transitions = len(transitionSpectra)

        # Define a list of distinct colors
        if n_transitions <=20 and n_transitions > 2:
            colors = Category20[len(transitionSpectra)]
        elif n_transitions <=2 and n_transitions > 0:
            colors = Category20[3]
        elif n_transitions == 1:
            colors = ['black']
        else:
            colors = Viridis256[len(transitionSpectra)]

        # Tooltips for interactive information
        TOOLTIPS = [
                ("index", "$index"),
                ("(mz,int)", "(@x{0.00}, @y)"),
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
            for precursorSpectrum in precursorSpectra:
                label = precursorSpectrum.label
                line = self.process_spectra(p, precursorSpectrum, label, transitionGroup=transitionGroup)
                legend_items.append((label, [line]))

        if self.include_ms2:
            for i, transitionSpectrum in enumerate(transitionSpectra):
                label = transitionSpectrum.label
                line = self.process_spectra(p, transitionSpectrum, label, color=colors[i], line_type='solid', is_precursor=False, transitionGroup=transitionGroup)
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
