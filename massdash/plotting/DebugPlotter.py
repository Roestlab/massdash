"""
massdash/plotting/GenericPlotter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Optional, Literal

# Plotting modules
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool, ColumnDataSource, PrintfTickFormatter, LegendItem, Legend
from bokeh.palettes import Category20



class DebugPlotter:
    def __init__(self):
        self.fig = None
        
    def plot(self, df):
        # Create a new plot
        p = figure(title='Retention time transformation', x_axis_label='original RT [s]', y_axis_label='Delta RT [s]',
           tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save'])

        unique_filenames = df['filename'].unique()
        colors = Category20[len(unique_filenames)]

        legend_it = []
        file_number = 1
        for filename, grouped_df in df.groupby('filename'):
            
            color = colors[file_number-1]
            print(f"File {file_number}: {filename} | color: {color}")
            # Add the scatter plot
            source = ColumnDataSource(grouped_df)
            renderer = p.scatter('experiment_rt', 'library_rt', source=source, size=10, alpha=0.5, color=color)
            legend_it.append((f"File {file_number}", [renderer]))
            file_number += 1

        # Configure the minimal hover tool
        hover_minimal = HoverTool(tooltips=[
            ('original RT', '@experiment_rt{0.0}'),
            ('Delta RT', '@library_rt{0.0}'),
            ('Peptide Sequence', '@ModifiedPeptideSequence')
        ], name="Minimal Hover")
        p.add_tools(hover_minimal)

        # Configure the detailed hover tool
        hover_detailed = HoverTool(tooltips=[
            ('Protein ID', '@ProteinId'),
            ('Precursor m/z', '@PrecursorMz{0.4}'),
            ('Precursor Charge', '@PrecursorCharge'),
            ('Normalized Retention Time', '@NormalizedRetentionTime{0.2}'),
            ('Precursor Ion Mobility', '@PrecursorIonMobility{0.6}'),
            ('Filename', '''<div style="width:200px; word-wrap:break-word;">@filename</div>''')
        ], name="Detailed Hover")
        p.add_tools(hover_detailed)

        # Add a legend for the filename
        legend = Legend(items=legend_it)
        legend.click_policy="mute"
        legend.label_text_font_size = '8pt'
        p.add_layout(legend, 'right')

        # Format the tick labels to remove scientific notation
        p.xaxis.formatter = PrintfTickFormatter(format='%.2f')
        p.yaxis.formatter = PrintfTickFormatter(format='%.2f')
        return p