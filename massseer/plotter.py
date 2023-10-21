import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend,Title
from bokeh.palettes import Category20, Viridis256
from scipy.signal import savgol_filter
import numpy as np


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
    def __init__(self, data, peptide_transition_list, trace_annotation, title, subtitle, x_axis_label="Retention Time", y_axis_label="Intensity", smoothing_dict={'type':'sgolay', 'sgolay_polynomial_order':3, 'sgolay_frame_length':11}, plot_type='matplotlib'):
        
        self.data = data
        self.peptide_transition_list = peptide_transition_list
        self.trace_annotation = trace_annotation 
        self.title = title
        self.subtitle = subtitle
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.smoothing_dict = smoothing_dict
        self.plot_type = plot_type

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
