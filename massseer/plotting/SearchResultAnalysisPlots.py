from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import Legend, HoverTool
import numpy as np
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