from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import Legend, HoverTool, ColumnDataSource, FactorRange, Whisker
from bokeh.palettes import Category10
import plotly.express as px
import matplotlib.pyplot as plt
from upsetplot import UpSet
# https://discuss.streamlit.io/t/cannot-change-matplotlib-figure-size/10295/6
from io import BytesIO
from itertools import cycle
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

class SearchResultAnalysisPlots:
    def __init__(self) -> None:
        self.df = None
        
    def plot_score_distributions(self, df, score_column="SCORE"):
        top_targets = df[df["DECOY"] == 0][score_column].values
        top_decoys = df[df["DECOY"] == 1][score_column].values

        # Create a Bokeh figure
        p1 = figure(x_axis_label=score_column, y_axis_label="# of groups", width=600, height=450)

        # Plot histograms for targets
        hist_targets, edges_targets = np.histogram(top_targets, bins=20)
        hist_targets_handle = p1.quad(top=hist_targets, bottom=0, left=edges_targets[:-1], right=edges_targets[1:], color="blue", alpha=0.7)

        # Plot histograms for decoys
        hist_decoys, edges_decoys = np.histogram(top_decoys, bins=20)
        hist_decoys_handle = p1.quad(top=hist_decoys, bottom=0, left=edges_decoys[:-1], right=edges_decoys[1:], color="red", alpha=0.6)
        
        hover1 = HoverTool(renderers=[hist_targets_handle, hist_decoys_handle],
                        tooltips=[(f"{score_column}", "@left"), ("Count", "@top")])
        p1.add_tools(hover1)
        
        p1.add_layout(Legend(items=[("Target", [hist_targets_handle]), ("Decoy", [hist_decoys_handle])]), 'right')
        p1.legend.click_policy="mute"

        # Create a Bokeh figure for density plot
        p2 = figure(x_axis_label=score_column, y_axis_label="Density", width=600, height=450)

        # Plot density curves
        xs = np.linspace(min(np.concatenate((top_targets, top_decoys))), max(np.concatenate((top_targets, top_decoys))), 200)
        dens_targets_handle = p2.line(xs, gaussian_kde(top_targets)(xs), line_color="blue", line_width=2)
        dens_decoys_handle = p2.line(xs, gaussian_kde(top_decoys)(xs), line_color="red", line_width=2)

        hover2 = HoverTool(renderers=[dens_targets_handle, dens_decoys_handle],
                        tooltips=[(f"{score_column}", "@x"), ("Density", "@y")])
        p2.add_tools(hover2)

        p2.add_layout(Legend(items=[("Target", [dens_targets_handle]), ("Decoy", [dens_decoys_handle])]), 'right')
        p2.legend.click_policy="mute"
        
        # Create a grid layout
        grid = gridplot([p1, p2], ncols=2, sizing_mode="stretch_both")

        # Show the plot
        return grid
    
    

    def plot_identifications(self, df, aggregate=True):
        # Get best peptide identification per filename, entry using the min Qvalue
        df = df[df.groupby(["filename", "entry", "ModifiedPeptideSequence"])["Qvalue"].transform(min) == df["Qvalue"]]
        if aggregate:
            # Get number of rows grouped by column entry and filename
            counts = df.groupby(["entry", "filename"]).size().reset_index(name='count')
            counts = counts.groupby(["entry"])["count"].agg(count=np.median, std=np.std).reset_index()
            
            # Create the figure
            p = figure(x_range=FactorRange(*counts["entry"].unique()), plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "Entry"
            p.yaxis.axis_label = "Number of identifications"

            # Create a color cycle for bars
            color_cycle = cycle(Category10[10])

            legend_items = []
            for i, entry in enumerate(counts["entry"].unique()):
                # Get the counts for the current entry
                counts_entry = counts[counts["entry"] == entry]
                upper = counts_entry["count"] + counts_entry["std"]
                lower = counts_entry["count"] - counts_entry["std"]

                # Create a ColumnDataSource from the data
                source = ColumnDataSource(data=dict(x=counts_entry["entry"], y=counts_entry["count"], upper=upper, lower=lower))

                # Get the next color from the cycle
                color = next(color_cycle)

                # Add the bar glyphs with unique color
                bar = p.vbar(x="x", top="y", width=0.9, source=source, color=color)

                # Add the error bars (standard deviation)
                whisker = Whisker(source=source, base="x", upper="upper", lower="lower", line_color="black", line_width=1.5, level="annotation")
                p.add_layout(whisker)

                # Add the legend item
                legend_items.append((entry, [bar]))
                
            # Set y-axis to max upper std value + padding of 50
            p.y_range.end = max(upper) * 1.2
        else:
            counts = df.groupby(["entry", "filename"]).size().reset_index(name='count')

            # Create the figure
            p = figure(x_range=FactorRange(*counts["filename"].unique()), plot_height=450, plot_width=600)

            # Axis titles
            p.xaxis.axis_label = "Filename"
            p.yaxis.axis_label = "Number of identifications"

            # Create a color cycle for bars
            color_cycle = cycle(Category10[10])

            legend_items = []
            for i, entry in enumerate(counts["entry"].unique()):
                # Get the counts for the current entry
                counts_entry = counts[counts["entry"] == entry]

                # Create a ColumnDataSource from the data
                source = ColumnDataSource(data=dict(x=counts_entry["filename"], y=counts_entry["count"]))

                # Get the next color from the cycle
                color = next(color_cycle)

                # Add the bar glyphs with unique color
                bar = p.vbar(x="x", top="y", width=0.9, source=source, color=color)

                # Add the legend item
                legend_items.append((entry, [bar]))

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
                    
    def plot_quantifications(self, df):
        """
        Plot violin-boxplot for quantifications
        """
        # Take the log2 of the Intensity column
        df['log2_intensity'] = np.log2(df['Intensity'])
        
        # Get unique entries and sort them
        entries = df["entry"].unique()
        entries.sort()

        p = px.violin(df, x="entry", y="log2_intensity", color="entry", box=True, labels = {"log2_intensity": "log2(Intensity)", "entry": "Entry"}, category_orders={"entry": entries})
        
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
    def compute_coefficient_of_variation(df):
        """
        Compute coefficient of variation of intensity per entry per ModifiedPeptideSequence across filenames
        """
        # Group by entry, ModifiedPeptideSequence, and filename
        grouped_df = df.groupby(["entry", "ModifiedPeptideSequence", "filename"])["Intensity"].mean().reset_index()

        # Calculate mean and standard deviation for each group
        agg_df = grouped_df.groupby(["entry", "ModifiedPeptideSequence"]).agg(
            mean_intensity=pd.NamedAgg(column="Intensity", aggfunc="mean"),
            std_intensity=pd.NamedAgg(column="Intensity", aggfunc="std")
        ).reset_index()

        # Calculate coefficient of variation
        agg_df["coefficient_of_variation"] = agg_df["std_intensity"] / agg_df["mean_intensity"] * 100

        return agg_df

    def plot_coefficient_of_variation(self, df):
        """
        Plot violin-boxplot for coefficient of variation of intensity per entry per ModifiedPeptideSequence
        """
        # Compute coefficient of variation
        agg_df = self.compute_coefficient_of_variation(df)

        # Get unique entries and sort them
        entries = agg_df["entry"].unique()
        entries.sort()
        
        # Plot violin-boxplot
        p = px.violin(agg_df, x="entry", y="coefficient_of_variation", color="entry", box=True, labels = {"coefficient_of_variation": "Coefficient of variation (%)", "entry": "Entry"}, category_orders={"entry": entries})

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

    def plot_venn_diagram(self, df):
        """
        Create a matplotlib Venn diagram comparing overlapping ModifiedPeptideSequence's between entries
        (with unique ModifiedPeptideSequence across filenames)
        """
        # Group by entry and ModifiedPeptideSequence, keeping only unique ModifiedPeptideSequence across filenames
        grouped_df = df.groupby(["entry", "ModifiedPeptideSequence"])["filename"].nunique().reset_index()
        unique_df = grouped_df[grouped_df["filename"] == 1]
        
        # Get unique entries and sort them
        entries = unique_df["entry"].unique()
        entries.sort()
        if len(entries) == 1:
            raise ValueError("Only one entry found. Cannot create Venn diagram.")
        elif len(entries) == 2:
            from matplotlib_venn import venn2 as venn
        elif len(entries) == 3:
            from matplotlib_venn import venn3 as venn
        else:
            raise ValueError("More than 3 entries found. Cannot create Venn diagram.")

        # Create a dictionary to store unique ModifiedPeptideSequence's for each entry
        entry_unique_dict = {}
        for entry in entries:
            entry_unique_dict[entry] = set(unique_df[unique_df["entry"] == entry]["ModifiedPeptideSequence"])


        # Create a matplotlib Venn diagram
        p = venn(entry_unique_dict.values(), set_labels=entry_unique_dict.keys())
        
        return p

    def plot_upset_diagram(self, df, context_cols="ModifiedPeptideSequence"):
        """
        Create an UpSet plot showing the intersection of ModifiedPeptideSequence's between entries
        (with unique ModifiedPeptideSequence across filenames)
        """

        unique_df = df.drop_duplicates(["entry", context_cols])

        # Create a DataFrame suitable for UpSet plot
        entry_df_list = []
        for entry in unique_df["entry"].unique():
            entry_modified_peptides = set(unique_df[unique_df["entry"] == entry][context_cols])
            entry_modified_peptides = list(entry_modified_peptides)
            tmp_df = pd.DataFrame({entry: True, context_cols: entry_modified_peptides})
            entry_df_list.append(tmp_df)
        
        # Merge all DataFrames on ModifiedPeptideSequence by outer join
        upset_data = entry_df_list[0]
        for i in range(1, len(entry_df_list)):
            upset_data = upset_data.merge(entry_df_list[i], on=context_cols, how="outer")
            
        # Replace NaN with False
        upset_data = upset_data.fillna(False)
        
        # Make sets index for the dataframe
        upset_data = upset_data.set_index(list(unique_df["entry"].unique()))

        # Create the UpSet plot
        upset = UpSet(upset_data)

        fig = plt.figure(figsize=(6, 4))
        upset.plot(fig = fig)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        return buf