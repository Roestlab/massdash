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

# Internal
from massseer.util import PEAK_PICKING_ALGORITHMS
from massseer.peak_picking import perform_chromatogram_peak_picking
from massseer.chromatogram_data_handling import compute_consensus_chromatogram, normalize
from massseer.SqlDataAccess import OSWDataAccess


class Plotter:
    """
    A class for creating static and interactive plots of chromatographic data.

    Attributes:
    -----------
    data : list
        A list of tuples containing retention time and intensity data for each trace.
    peptide_transition_list : pandas.DataFrame or None
        A DataFrame containing information about the peptide transitions, including precursor and product m/z values and charges.
    trace_annotation : list
        A list of strings containing annotations for each trace.
    title : str
        The main title of the plot.
    subtitle : str
        The subtitle of the plot.
    x_axis_label : str
        The label for the x-axis of the plot.
    y_axis_label : str
        The label for the y-axis of the plot.
    smoothing_dict : dict
        A dictionary containing parameters for smoothing the intensity data.
    plot_type : str
        The type of plot to create ('matplotlib' or 'bokeh').

    Methods:
    --------
    create_static_plot()
        Creates a static plot of the chromatographic data using matplotlib.
    create_interactive_plot()
        Creates an interactive plot of the chromatographic data using bokeh.
    plot()
        Creates a static or interactive plot of the chromatographic data depending on the plot_type attribute.
    """
    def __init__(self, data, peptide_transition_list, trace_annotation, title, subtitle, x_axis_label="Retention Time", y_axis_label="Intensity", smoothing_dict={'type':'sgolay', 'sgolay_polynomial_order':3, 'sgolay_frame_length':11}, plot_type='matplotlib', x_range=None, y_range=None, scale_intensity=False):
        
        self.data = data
        self.peptide_transition_list = peptide_transition_list
        self.trace_annotation = trace_annotation 
        self.title = title
        self.subtitle = subtitle
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.smoothing_dict = smoothing_dict
        self.plot_type = plot_type
        self.x_range = x_range
        self.y_range = y_range
        self.scale_intensity = scale_intensity

    def create_static_plot(self):
        """
        Creates a static plot of the data in self.data.

        Returns:
        None
        """
        #############################
        ##  Create a static plot
        
        # Create a figure
        plt.figure(figsize=(4, 3))
        
        # Loop through the traces in chrom_data
        for i, trace in enumerate(self.data):
            retention_time = trace[0]
            intensity = trace[1]
            if self.smoothing_dict['type'] == 'sgolay':
                # Apply Savitzky-Golay smoothing to the intensity data
                smoothed_intensity = savgol_filter(intensity, window_length=self.smoothing_dict['sgolay_frame_length'], polyorder=self.smoothing_dict['sgolay_polynomial_order'])
            else:
                smoothed_intensity = np.array(intensity)
            # Set negative values in smoothed_intensity to 0
            smoothed_intensity = np.where(smoothed_intensity < 0, 0, smoothed_intensity)
            label = f'{self.trace_annotation[i]}'  # Create a label for each series
            plt.plot(retention_time, smoothed_intensity, label=label)
        
        # Customize the plot
        plt.title(self.subtitle)
        plt.suptitle(self.title)
        plt.xlabel(self.x_axis_label)
        plt.ylabel(self.y_axis_label)
        plt.legend()
        
        # Show the plot
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    def create_interactive_plot(self):
        """
        Creates an interactive plot using Bokeh library.

        Returns:
        Bokeh figure object: A Bokeh figure object containing the interactive plot.
        """
        # Define a list of distinct colors
        if len(self.trace_annotation) <=20 and len(self.trace_annotation) > 1:
            colors = Category20[len(self.trace_annotation)]
        elif len(self.trace_annotation) ==1:
            colors = ['black']
        else:
            colors = Viridis256[len(self.trace_annotation)]

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
        subtitle = self.subtitle
        p.add_layout(Title(text=subtitle, text_font_style="italic"), 'above')

        # Create a legend
        legend = Legend()

        # Create a list to store legend items
        legend_items = []

        # Use a list comprehension to count 'Precursor'
        precursor_trace_count = sum(1 for item in self.trace_annotation if 'Precursor' in item)


        # Loop through the traces in chrom_data
        for i, trace in enumerate(self.data):
            retention_time = trace[0]
            intensity = trace[1]

            if self.smoothing_dict['type'] == 'sgolay':
                # Apply Savitzky-Golay smoothing to the intensity data
                smoothed_intensity = savgol_filter(intensity, window_length=self.smoothing_dict['sgolay_frame_length'], polyorder=self.smoothing_dict['sgolay_polynomial_order'])
            else:
                smoothed_intensity = np.array(intensity)
            
            if self.scale_intensity:
                smoothed_intensity = np.array(normalize(smoothed_intensity.tolist()))

            # Set negative values in smoothed_intensity to 0
            smoothed_intensity = np.where(smoothed_intensity < 0, 0, smoothed_intensity)

            label = f'{self.trace_annotation[i]}'  # Create a label for each series
            if 'Precursor' in label and self.peptide_transition_list is not None:
                precursor_mz_values = self.peptide_transition_list.PRECURSOR_MZ.to_list()[0]
                product_mz_values = "NULL"
                product_charge_values = "NULL"
            elif 'Precursor' not in label and self.peptide_transition_list is not None:   
                precursor_mz_values = self.peptide_transition_list.PRECURSOR_MZ.to_list()[i-precursor_trace_count]
                product_mz_values = self.peptide_transition_list.PRODUCT_MZ.to_list()[i-precursor_trace_count]
                product_charge_values = self.peptide_transition_list.PRODUCT_CHARGE.to_list()[i-precursor_trace_count]
            else:
                precursor_mz_values = "NULL"
                product_mz_values = "NULL"
                product_charge_values = "NULL"


            # Create a data source for the smoothed intensity data
            source = ColumnDataSource(data={
                  'x': retention_time,
                  'y': smoothed_intensity,
                  'precursor_mz': [precursor_mz_values] * len(retention_time),
                  'product_mz': [product_mz_values] * len(retention_time),
                  'product_charge': [product_charge_values] * len(retention_time)
              })
            # Plot the smoothed intensity data
            if 'Precursor' in label:
                line = p.line('x', 'y', source=source, line_color="black", line_width=2, line_dash="dashed")
            else:   
                line = p.line('x', 'y', source=source, line_color=colors[i], line_width=2)

            # Add the line to the legend items
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

        # Show the plot
        # show(p)
        return(p)
    def plot(self):
            """
            Plot the data using either matplotlib or bokeh depending on the plot_type attribute.

            Returns:
            - If plot_type is 'matplotlib', returns a static plot.
            - If plot_type is 'bokeh', returns an interactive plot.
            - If plot_type is invalid, prints an error message and returns None.
            """
            if self.plot_type == 'matplotlib':
                return self.create_static_plot()
            elif self.plot_type == 'bokeh':
                return self.create_interactive_plot()
            else:
                print("Invalid plot type. Use 'matplotlib' or 'bokeh'.")

class ChromDataDrawer:
    def __init__(self):
        """
        Initializes a ChromDataDrawer object with empty lists for chrom_data_all and trace_annotation_all, and a None value for plot_obj.
        """
        self.chrom_data_all = []
        self.trace_annotation_all = []
        self.plot_obj = None

    def draw_chrom_data(self, sqmass_file_path, chrom_data, include_ms1, include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, smoothing_dict={'type':'sgolay', 'sgolay_polynomial_order':3, 'sgolay_frame_length':11}, x_range=None, y_range=None, scale_intensity=False):
        """
        Adds chromatogram data to the ChromDataDrawer object's chrom_data_all and trace_annotation_all lists, and generates a plot using the Plotter class.

        Parameters:
        sqmass_file_path (str): The file path of the sqmass file.
        chrom_data (dict): A dictionary containing the chromatogram data.
        include_ms1 (bool): Whether to include MS1 data in the plot.
        include_ms2 (bool): Whether to include MS2 data in the plot.
        peptide_transition_list (pandas.DataFrame): A pandas DataFrame containing information about peptide transitions.
        selected_peptide (str): The selected peptide.
        selected_precursor_charge (int): The charge of the selected precursor.
        smoothing_dict (dict): A dictionary containing parameters for smoothing the data.
        x_range (tuple): A tuple containing the x-axis range for the plot.
        y_range (tuple): A tuple containing the y-axis range for the plot.

        Returns:
        self (ChromDataDrawer): The ChromDataDrawer object.
        """
        if include_ms1:
            self.chrom_data_all = self.chrom_data_all + chrom_data[sqmass_file_path]['ms1'][0]
            self.trace_annotation_all = self.trace_annotation_all + chrom_data[sqmass_file_path]['ms1'][1]

        if include_ms2:
            self.chrom_data_all = self.chrom_data_all + chrom_data[sqmass_file_path]['ms2'][0]
            self.trace_annotation_all = self.trace_annotation_all + chrom_data[sqmass_file_path]['ms2'][1]

        if len(self.chrom_data_all) != 0 and len(self.trace_annotation_all) != 0:
            plotter = Plotter(
                self.chrom_data_all,
                peptide_transition_list=peptide_transition_list[peptide_transition_list.PRODUCT_DETECTING == 1],
                trace_annotation=self.trace_annotation_all,
                title=os.path.basename(sqmass_file_path),
                subtitle=f"{selected_peptide}_{selected_precursor_charge}",
                smoothing_dict=smoothing_dict,
                plot_type='bokeh',
                x_range=x_range,
                y_range=y_range,
                scale_intensity=scale_intensity
            )

            # Generate the plot
            self.plot_obj = plotter.plot()

        return self

    def draw_consensus_chrom_data(self, consensus_chrom_mode, averaged_chrom_data, plot_title, selected_peptide, selected_precursor_charge, smoothing_dict={'type':'sgolay', 'sgolay_polynomial_order':3, 'sgolay_frame_length':11}, x_range=None, y_range=None):
        """
        Draws consensus chromatogram data for a selected peptide and precursor charge.

        Args:
            consensus_chrom_mode (str): The consensus chromatogram mode.
            averaged_chrom_data (dict): The averaged chromatogram data.
            smoothing_dict (dict): The smoothing dictionary.
            plot_title (str): The title of the plot.
            selected_peptide (str): The selected peptide.
            selected_precursor_charge (int): The selected precursor charge.
            x_range (tuple): The x-axis range of the plot.
            y_range (tuple): The y-axis range of the plot.

        Returns:
            self: The updated object.
        """
        self.chrom_data_all = averaged_chrom_data
        self.trace_annotation_all = [consensus_chrom_mode]  

        averaged_plotter = Plotter(self.chrom_data_all, peptide_transition_list=None, trace_annotation=self.trace_annotation_all, title=plot_title, subtitle=f"{selected_peptide}_{selected_precursor_charge}", smoothing_dict=smoothing_dict,  plot_type='bokeh', x_range=x_range, y_range=y_range)

        averaged_plot_obj = averaged_plotter.plot()

        self.plot_obj = averaged_plot_obj

        return self


    def draw_peak_boundaries(self, do_peak_picking, chromatogram_type='regular', peak_picker=None, osw_file_path=None, sqmass_file_path=None, selected_peptide=None, selected_precursor_charge=None):
        """
        Draws peak boundaries on the plot using the ChromDataDrawer object's plot_obj and the perform_chromatogram_peak_picking function.

        Parameters:
        do_peak_picking (str): The type of peak picking to perform.
        chromatogram_type (str): One of 'regular' of 'consensus'
        do_smoothing (bool): Whether to perform smoothing on the data.
        smoothing_dict (dict): A dictionary containing parameters for smoothing the data.

        Returns:
        self (ChromDataDrawer): The ChromDataDrawer object.
        """
        dark2_palette = ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02', '#A6761D', '#666666']
        if do_peak_picking == 'PeakPickerMRM':
            peak_features = perform_chromatogram_peak_picking(self.chrom_data_all, peak_picker, merged_peak_picking=True)
            
            
            for i in range(len(peak_features['leftWidth'])):
                y_bottom = [0] 
                self.plot_obj.vbar(x=peak_features['leftWidth'][i], bottom=y_bottom, top=peak_features['IntegratedIntensity'][i], width=0.1, color=dark2_palette[i], line_color=dark2_palette[i])
                self.plot_obj.vbar(x=peak_features['rightWidth'][i], bottom=y_bottom, top=peak_features['IntegratedIntensity'][i], width=0.1, color=dark2_palette[i], line_color=dark2_palette[i])
        elif do_peak_picking == "OSW-PyProphet" and chromatogram_type=='regular':
            print("Info: Getting OSW boundaries")
            print(osw_file_path)
            osw = OSWDataAccess(osw_file_path)
            osw_features = osw.getRunPrecursorPeakBoundaries(os.path.splitext(os.path.basename(sqmass_file_path))[0], selected_peptide, 
            selected_precursor_charge)

            

            for i in range(osw_features.shape[0]):
                source = ColumnDataSource(data = {
                    'Intensity' : [osw_features['Intensity'][i]],
                    'leftWidth'   : [osw_features['leftWidth'][i]],
                    'rightWidth'   : [osw_features['rightWidth'][i]],
                    'peakgroup_rank' : [osw_features['peakgroup_rank'][i]],
                    'ms2_mscore' : [osw_features['ms2_mscore'][i]],
                    'bottom_int'    : [0]})
                # Left border
                leftWidth_line = self.plot_obj.vbar(x='leftWidth', bottom='bottom_int', top='Intensity', width=0.1, color=dark2_palette[i], line_color=dark2_palette[i], source=source)
                # Right border
                self.plot_obj.vbar(x='rightWidth', bottom='bottom_int', top='Intensity', width=0.1, color=dark2_palette[i], line_color=dark2_palette[i], source=source)
                # Add a point to the left border to attached the hover tool to
                leftWidth_apex_point = self.plot_obj.circle(source=source, x='leftWidth', y='Intensity', name='leftWidth_apex_point', alpha=0) 


            # Create a HoverTool
            hover = HoverTool(names=['leftWidth_apex_point'],
                tooltips=[
                    ("Intensity", "@Intensity"),
                    ("Left Width", "@leftWidth{0.00}"),
                    ("Right Width", "@rightWidth{0.00}"),
                    ("Peak Group Rank", "@peakgroup_rank"),
                    ("MS2 m-score", "@ms2_mscore"),
                ]
            )
            # hover.renderers = [leftWidth_apex_point]
            # Add the HoverTool to your plot
            self.plot_obj.add_tools(hover)

        return self

def draw_single_chrom_data(sqmass_file_path, massseer_gui, chrom_data, include_ms1, include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, smoothing_dict, x_range, y_range, scale_intensity, algo_settings):
    """
    Draws a single chromatogram plot with optional peak picking and smoothing.

    Args:
        sqmass_file_path (str): The path to the SqMass file.
        chrom_data (dict): A dictionary containing the chromatogram data.
        include_ms1 (bool): Whether or not to include MS1 data in the plot.
        include_ms2 (bool): Whether or not to include MS2 data in the plot.
        peptide_transition_list (list): A list of peptide transitions to include in the plot.
        selected_peptide (str): The selected peptide to highlight in the plot.
        selected_precursor_charge (int): The charge state of the selected precursor.
        smoothing_dict (dict): A dictionary containing the smoothing parameters.
        x_range (tuple): A tuple containing the x-axis range for the plot.
        y_range (tuple): A tuple containing the y-axis range for the plot.
        do_peak_picking (str): The peak picking algorithm to use (if any).
        do_smoothing (bool): Whether or not to apply smoothing to the data.

    Returns:
        ChromDataDrawer: An instance of the ChromDataDrawer class containing the plot data.
    """
    chrom_data_drawer = ChromDataDrawer()
    chrom_data_drawer.draw_chrom_data(sqmass_file_path, chrom_data, include_ms1, include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, smoothing_dict, x_range, y_range, scale_intensity)

    if algo_settings.do_peak_picking == "OSW-PyProphet":
        print(f"Peak Picking: {algo_settings.do_peak_picking}")
        chrom_data_drawer.draw_peak_boundaries(algo_settings.do_peak_picking, 'regular', None, massseer_gui.osw_file_path, sqmass_file_path, selected_peptide, selected_precursor_charge)
    elif algo_settings.do_peak_picking in PEAK_PICKING_ALGORITHMS:
        print(f"Peak Picking: {algo_settings.do_peak_picking}")
        chrom_data_drawer.draw_peak_boundaries(algo_settings.do_peak_picking, 'regular', algo_settings.PeakPickerMRMParams.peak_picker)
    
    return chrom_data_drawer


# @st.cache_resource(show_spinner="Drawing chromatograms...")
def draw_many_chrom_data(sqmass_file_path_list, massseer_gui,  chrom_data, include_ms1, include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, smoothing_dict, x_range, y_range, scale_intensity, _algo_settings, threads ):
    """
    Draws chromatograms for multiple files and returns a dictionary with the results.

    Parameters:
    -----------
    sqmass_file_path_list : list of str
        List of paths to the SqMass files to be processed.
    chrom_data : dict
        Dictionary containing the chromatogram data for each file.
    include_ms1 : bool
        Whether to include MS1 data in the plot.
    include_ms2 : bool
        Whether to include MS2 data in the plot.
    peptide_transition_list : list of str
        List of peptide transitions to be plotted.
    selected_peptide : str
        Peptide sequence to be highlighted in the plot.
    selected_precursor_charge : int
        Precursor charge state to be highlighted in the plot.
    smoothing_dict : dict
        Dictionary containing the smoothing parameters for each transition.
    x_range : tuple of float
        Tuple containing the x-axis range for the plot.
    y_range : tuple of float
        Tuple containing the y-axis range for the plot.
    do_peak_picking : bool
        Whether to perform peak picking on the data.
    do_smoothing : bool
        Whether to perform smoothing on the data.
    threads : int
        Number of threads to use for processing.

    Returns:
    --------
    output : dict
        Dictionary containing the Bokeh plot objects for each file.
    """
    print(f"Peak Picking: {_algo_settings.do_peak_picking}")
    # Unfortunately we cannot perform mulltiprocessing because the bokeh object is not serializble
    output = {}
    for sqmass_file_path in sqmass_file_path_list:
        res = draw_single_chrom_data(sqmass_file_path, massseer_gui, chrom_data, include_ms1, include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, smoothing_dict, x_range, y_range, scale_intensity, _algo_settings)
        output[sqmass_file_path] = res


    return output

def draw_single_consensus_chrom(sqmass_file_path, selected_peptide, selected_precursor_charge, do_consensus_chrom, consensus_chrom_mode, chrom_data_all, chrom_data_global, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold, smoothing_dict, x_range, y_range, algo_settings):
    """
    Draw a single consensus chromatogram.

    Args:
        sqmass_file_path (str): The path to the sqmass file.
        selected_peptide (str): The selected peptide.
        selected_precursor_charge (int): The selected precursor charge.
        do_consensus_chrom (str): The type of consensus chromatogram to generate.
        consensus_chrom_mode (str): The mode to use for generating the consensus chromatogram.
        chrom_data_all (list): The chromatogram data for all runs.
        chrom_data_global (list): The chromatogram data for all runs combined.
        scale_intensity (bool): Whether to scale the intensity of the chromatogram.
        percentile_start (float): The percentile to start scaling the intensity from.
        percentile_end (float): The percentile to end scaling the intensity at.
        threshold (float): The threshold for peak detection.
        auto_threshold (bool): Whether to automatically determine the threshold for peak detection.
        smoothing_dict (dict): The smoothing parameters to use for peak detection.
        x_range (tuple): The x-axis range to plot.
        y_range (tuple): The y-axis range to plot.
        do_peak_picking (str): The peak picking algorithm to use.
        do_smoothing (bool): Whether to smooth the chromatogram data.

    Returns:
        ChromDataDrawer: The object used to draw the consensus chromatogram.
    """
    ## Generate consensus chromatogram
    if do_consensus_chrom == 'run-specific':
        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        plot_title = os.path.basename(sqmass_file_path)
    elif do_consensus_chrom == 'global':
        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_global, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
        plot_title = 'Global Across-Run Consensus Chromatogram'

    chrom_data_drawer = ChromDataDrawer()
    chrom_data_drawer.draw_consensus_chrom_data(consensus_chrom_mode, averaged_chrom_data, plot_title, selected_peptide, selected_precursor_charge, smoothing_dict, x_range, y_range)    

    if algo_settings.do_peak_picking in PEAK_PICKING_ALGORITHMS and algo_settings.do_peak_picking != "OSW-PyProphet":
        chrom_data_drawer.draw_peak_boundaries(algo_settings.do_peak_picking, 'consensus', algo_settings.PeakPickerMRMParams.peak_picker)
    
    return chrom_data_drawer

# @st.cache_resource(show_spinner="Drawing consensus chromatograms...")
def draw_many_consensus_chrom(sqmass_file_path_list, selected_peptide, selected_precursor_charge, do_consensus_chrom, consensus_chrom_mode, _chrom_plot_objs, chrom_data_global, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold, smoothing_dict, x_range, y_range, _algo_settings, threads):
    """
    Draws consensus chromatograms for multiple input files.

    Args:
        sqmass_file_path_list (list): List of file paths to sqMass files.
        selected_peptide (str): Sequence of the selected peptide.
        selected_precursor_charge (int): Charge state of the selected peptide.
        do_consensus_chrom (bool): Whether to draw consensus chromatograms.
        consensus_chrom_mode (str): Mode for drawing consensus chromatograms.
        _chrom_plot_objs (dict): Dictionary of ChromPlot objects.
        chrom_data_global (dict): Dictionary of global chromatogram data.
        scale_intensity (bool): Whether to scale the intensity of the chromatograms.
        percentile_start (float): Start percentile for scaling the intensity.
        percentile_end (float): End percentile for scaling the intensity.
        threshold (float): Threshold for peak detection.
        auto_threshold (bool): Whether to use automatic threshold for peak detection.
        smoothing_dict (dict): Dictionary of smoothing parameters.
        x_range (tuple): Tuple of x-axis range for the plot.
        y_range (tuple): Tuple of y-axis range for the plot.
        do_peak_picking (bool): Whether to perform peak picking.
        do_smoothing (bool): Whether to perform smoothing.
        threads (int): Number of threads to use for processing.

    Returns:
        dict: Dictionary of output data for each input file.
    """

    # Unfortunately we cannot perform mulltiprocessing because the bokeh object is not serializble
    output = {}
    for sqmass_file_path in sqmass_file_path_list:
        res = draw_single_consensus_chrom(sqmass_file_path, selected_peptide, selected_precursor_charge, do_consensus_chrom, consensus_chrom_mode, _chrom_plot_objs[sqmass_file_path].chrom_data_all, chrom_data_global, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold, smoothing_dict, x_range, y_range, _algo_settings)
        output[sqmass_file_path] = res

    return output