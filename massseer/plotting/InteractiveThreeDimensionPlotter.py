from typing import List, Tuple
import streamlit as st

# Data modules
import numpy as np
import pandas as pd
import math  
from scipy.interpolate import griddata
from scipy.signal import savgol_filter

# Plotting modules
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# Plotting
from massseer.plotting.GenericPlotter import PlotConfig
# Structs
from massseer.structs.FeatureMap import FeatureMap
# Utils
from massseer.util import check_streamlit

class InteractiveThreeDimensionPlotter:
    """
    Class for interactive three-dimensional plotting.
    
    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data for plotting.
        config (PlotConfig): The configuration for plotting.
        
    """
    def __init__(self, config: PlotConfig):
        self.config = config
        self.fig = None # set by plot method
        
    def plot(self, featureMap: FeatureMap):
        """
        Plot the data based on the configuration settings.

        Returns:
            plots (list): List of plots generated based on the configuration settings.
        """
        if self.config.type_of_3d_plot == "3D Scatter Plot" and self.config.aggregate_mslevels:
            plots = self.plot_3d_scatter(featureMap, num_rows=1, num_cols=1)
        elif self.config.type_of_3d_plot == "3D Scatter Plot" and not self.config.aggregate_mslevels:
            plots = self.plot_3d_scatter(featureMap, num_cols = self.config.num_plot_columns)
        elif self.config.type_of_3d_plot == "3D Surface Plot" and not self.config.aggregate_mslevels:
            plots = self.plot_individual_3d_surface(featureMap, self.config.num_plot_columns)
        elif self.config.type_of_3d_plot == "3D Line Plot" and not self.config.aggregate_mslevels:
            plots = self.plot_3d_vline(featureMap)
        self.fig = plots
        return plots
    
    def plot_3d_scatter(self, featureMap: FeatureMap, num_rows: int = -1, num_cols: int = 2) -> go.Figure:
        """
        Make a general 3D scatter plot with options for individual or overall plots.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            num_cols (int, optional): Number of columns in the subplot grid. Defaults to 2.
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to True.
            include_ms2 (bool, optional): Whether to include MS2 data. Defaults to True.

        Returns:
            go.Figure: The Plotly Figure object.
        """
        if self.config.context == "streamlit":
            marker_size = 5
            height_scale_factor = width_scale_factor = 800
            spacing = 0.05
            ratio = 1
        elif self.config.context == "jupyter": 
            marker_size = 2
            ratio = 0.75
            if num_rows == 1:
                height_scale_factor = width_scale_factor = 800
                spacing = 0.01
            else: # num_rows == -1
                height_scale_factor = 400
                width_scale_factor = 150
                spacing = 0.01
        else:
            raise ValueError(f"Error: Invalid context type: {self.config.context}, must be either 'streamlit' or 'jupyter'")

        if num_rows == -1:
            # Determine the number of unique annotations
            num_rows = num_annotations = len(featureMap['Annotation'].unique())
            subplot_titles = featureMap['Annotation'].unique()
            specs = [[{'type': 'scatter3d'}] * num_cols for _ in range(num_annotations)]
        elif num_rows == 1 and num_cols == 1:
            num_annotations = 1
            subplot_titles = ['']
            specs = [[{'type': 'scatter3d'}]]

        # Create a subplot with 3D scatter plots for each group
        subfig = make_subplots(
            rows=num_rows, cols=num_cols,
            subplot_titles=subplot_titles,
            specs=specs,
            horizontal_spacing=spacing, vertical_spacing=spacing
        )

        # Create a 3D scatter plot for each group
        for i, (group_key, group_df) in enumerate(featureMap.feature_df.sort_values(by=['ms_level', 'Annotation']).groupby(['ms_level', 'Annotation'])):
            if not self.config.include_ms1 and group_key[0] == 1:
                continue

            if not self.config.include_ms2 and group_key[0] == 2:
                continue

            x = group_df['rt'].values
            y = group_df['mz'].values
            if featureMap.has_im:
                z = group_df['im'].values
            intensity = group_df['int'].values  

            # Define color scale based on ms_level
            # Use 'Viridis' for ms_level = 1, 'Jet' for ms_level = 2
            colorscale = 'Viridis' if group_key[0] == 1 else 'Jet'  

            # Create a 3D scatter plot for each group
            trace = go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                marker=dict(size=marker_size, color=intensity, colorscale=colorscale),
                name=group_key[1]
            )

            if num_rows == 1 and num_cols == 1:
                row_num = 1
                col_num = 1
            else:
                # Calculate row and column numbers based on 1-indexing
                row_num = i // num_cols + 1  
                col_num = i % num_cols + 1 

            subfig.add_trace(trace, row=row_num, col=col_num)  
            
            scene = dict(aspectmode='manual',
                        aspectratio=dict(x=ratio, y=ratio, z=ratio),
                        camera=dict(eye=dict(x=1.25, y=1.25, z=1.25)),
                        xaxis_title = "RT",
                        yaxis_title = "MZ",
                        zaxis_title = "IM")
            
            subfig.update_scenes(scene, row=row_num, col=col_num)

        # Update the layout of the overall figure
        subfig.update_layout(
            height=num_annotations * height_scale_factor,
            width=num_annotations * width_scale_factor,
            showlegend=False
        )

        return subfig

    def plot_3d_vline(self, featureMap: FeatureMap) -> go.Figure:
        """
        Plot a 3D spectrum-chromatogram vertical line plot.

        Returns:
            fig (plotly.graph_objs._figure.Figure): The generated 3D vertical line plot.
        """
        # Step 1: Group DataFrame by 'Annotation' column
        grouped_df = featureMap.feature_df.groupby('Annotation')
        
        # Get unique values in 'Annotation' column
        unique_annotations = featureMap['Annotation'].unique()

        # Generate a list of unique colors using a Plotly color scale
        colors = px.colors.qualitative.Set1[:len(unique_annotations)]

        # Create a dictionary mapping unique annotations to colors
        annotation_color_dict = dict(zip(unique_annotations, colors))

        # Create a 3D scatter plot
        fig = go.Figure()
        
        # Iterate over groups and create scatter points
        for name, group in grouped_df:
            # Transform to vertical line data wiht no connections
            x_vert = []
            y_vert = []
            z_vert = []
            for x, y, z in zip(group['rt'], group['product_mz'], group['int']):
                for i in range(2):
                    x_vert.append(x)
                    y_vert.append(y,)
                    if i == 0:
                        z_vert.append(0)    
                    else:
                        z_vert.append(z)
                x_vert.append(None)
                y_vert.append(None)
                z_vert.append(None)           
            
            # Get the color for the current 'Annotation' value
            color = annotation_color_dict[name]

            # Create lines connecting the points
            fig.add_trace(go.Scatter3d(
                x=x_vert,
                y=y_vert,
                z=z_vert,
                mode='lines',
                line=dict(width=5, color=color),  # Adjust line width as needed
                name=name,
                legendgroup=name  # Ensure all traces of the same group share the same legend item
            ))

        # Add grid lines
        fig.update_layout(scene=dict(xaxis=dict(title='RT', nticks=4, gridcolor='rgb(255, 255, 255)', zerolinecolor='rgb(255, 255, 255)'),
                                    yaxis=dict(title='MZ', nticks=4, gridcolor='rgb(255, 255, 255)', zerolinecolor='rgb(255, 255, 255)'),
                                    zaxis=dict(title='Intensity', nticks=4, gridcolor='rgb(255, 255, 255)', zerolinecolor='rgb(255, 255, 255)')))

        # Update the layout of the overall figure
        fig.update_layout(
            height=900,
            width=800
        )
        
        # Default parameters which are used when `layout.scene.camera` is not provided
        camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.25, y=1.8, z=1.25)
        )
        fig.update_layout(scene_camera=camera)

        return fig
    
    def plot_individual_3d_surface(self, featureMap: FeatureMap, num_cols: int=2) -> go.Figure:
        """
        Plot individual 3D surface plots for each precursor and each product ion.
        
        Args:
            num_cols (int, optional): Number of columns in the subplot grid. Defaults to 2.
            
        Returns:
            go.Figure: The Plotly Figure object.
        """
        # Create a subplot with 3D surface plots for each group
        if self.config.context == "streamlit":
            horizontal_spacing = 0.05
            vertical_spacing = 0.05
            height_scale_factor = width_scale_factor = 800
        elif self.config.context == "jupyter":
            ratio = 0.75
            horizontal_spacing = 0.03
            vertical_spacing = 0.03
            height_scale_factor = 400
            num_cols = 2
            width_scale_factor = 150
        else:
            raise ValueError(f"Error: Invalid context type: {self.config.context}, must be either 'streamlit' or 'jupyter'")

        df = featureMap.feature_df
        subfig = make_subplots(rows=len(df['Annotation'].unique()), cols=num_cols,
                            subplot_titles=df['Annotation'].unique(),
                            specs=[[{'type': 'surface'}] * num_cols for _ in range(len(df['Annotation'].unique()))],
                            horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing)

        # Iterate over groups and create subplots
        for i, (group_key, group_df) in enumerate(df.sort_values(by=['ms_level', 'Annotation', 'product_mz']).groupby(['ms_level', 'Annotation', 'product_mz'])):
            if not self.config.include_ms1 and group_key[0] == 1:
                continue
            
            if not self.config.include_ms2 and group_key[0] == 2:
                continue
            
            if self.config.type_of_comparison == "retention time vs ion mobility":
                group_df = group_df.groupby(['rt', 'im']).agg({'int': 'sum'}).reset_index()
                x = group_df['rt'].values
                y = group_df['im'].values
                x_title, y_title, z_title = 'RT', 'IM', 'Intensity'
            elif self.config.type_of_comparison == "retention time vs m/z":
                group_df = group_df.groupby(['rt', 'mz']).agg({'int': 'sum'}).reset_index()
                x = group_df['rt'].values
                y = group_df['mz'].values
                x_title, y_title, z_title = 'RT', 'MZ', 'Intensity'
            elif self.config.type_of_comparison == "ion mobility vs m/z":
                group_df = group_df.groupby(['im', 'mz']).agg({'int': 'sum'}).reset_index()
                x = group_df['im'].values
                y = group_df['mz'].values
                x_title, y_title, z_title = 'IM', 'MZ', 'Intensity'
            elif self.config.type_of_comparison == "retention time vs ion mobility vs m/z":
                x = group_df['rt'].values
                y = group_df['mz'].values
                x_title, y_title, z_title = 'RT', 'MZ', 'IM'
            
            # Smooth
            if self.config.smoothing_dict['type'] == 'sgolay':
                try:
                    group_df['int'] = savgol_filter(group_df['int'].values, window_length=self.config.smoothing_dict['sgolay_frame_length'], polyorder=self.config.smoothing_dict['sgolay_polynomial_order'])
                except ValueError as ve:
                    if 'window_length must be less than or equal to the size of x' in str(ve):
                        error_message = f"Error: The specified window length for sgolay smoothing is too large for transition = {group_key[1]}. Try adjusting it to a smaller value."
                    else:
                        error_message = f"Error: {ve}"

                    if check_streamlit():
                        st.error(error_message)
                    else:
                        raise ValueError(error_message)
            elif self.config.smoothing_dict['type'] == 'none':
                pass
            
            if self.config.type_of_comparison == "retention time vs ion mobility vs m/z":
                z = group_df['im'].values
            else:  
                z = group_df['int'].values
            intensity = group_df['int'].values  # Assuming 'intensity' is the column representing intensity

            # Create a mesh grid
            x_unique = np.unique(x)
            y_unique = np.unique(y)
            x_grid, y_grid = np.meshgrid(x_unique, y_unique)
            
            z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')

            intensity_grid = griddata((x, y), intensity, (x_grid, y_grid), method='cubic')

            # Create a 3D surface plot for each group
            trace = go.Surface(x=x_grid, y=y_grid, z=z_grid, surfacecolor=intensity_grid, colorscale='Viridis', 
                            showlegend = False)
            row_num = math.floor(i / num_cols) + 1  # Calculate the row number based on the number of columns
            col_num = i % num_cols + 1  # Calculate the column number based on the number of columns
            subfig.add_trace(trace, row=row_num, col=col_num)  # Use the calculated row and column numbers
            
            subfig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                  highlightcolor="limegreen", project_z=True), 
                            showlegend = False, showscale=False)

            scene = dict(aspectmode='manual',
                        aspectratio=dict(x=ratio, y=ratio, z=ratio),
                        camera=dict(eye=dict(x=1.25, y=1.25, z=1.25)),
                        xaxis_title = x_title,
                        yaxis_title = y_title,
                        zaxis_title = z_title)
            
            subfig.update_scenes(scene, row=row_num, col=col_num)

        # Update the layout of the overall figure
        subfig.update_layout(height=len(df['Annotation'].unique()) * height_scale_factor,
                            width=len(df['Annotation'].unique()) * width_scale_factor, showlegend=False)
        
        subfig.update_coloraxes(showscale=False)

        return subfig
    
    def plot_individual_3d_mesh_cube(self, featureMap: FeatureMap, num_cols: int=2) -> go.Figure:
        """
        Plot individual 3D surface plots for each precursor and each product ion. (EXPERIMENTAL)
        
        Args:
            featureMap (FeatureMap): The FeatureMap object containing the data.
            num_cols (int, optional): Number of columns in the subplot grid. Defaults to 2.
            
        Returns:
            go.Figure: The Plotly Figure object.
        """
        # Create a subplot with 3D surface plots for each group
        subfig = make_subplots(rows=len(featureMap['Annotation'].unique()), cols=num_cols,
                            subplot_titles=featureMap['Annotation'].unique(),
                            specs=[[{'type': 'surface'}] * num_cols for _ in range(len(featureMap['Annotation'].unique()))],
                            horizontal_spacing=0.05, vertical_spacing=0.05)

        # Iterate over groups and create subplots
        for i, (group_key, group_df) in enumerate(featureMap.sort_values(by=['ms_level', 'Annotation', 'product_mz']).groupby(['ms_level', 'Annotation', 'product_mz'])):
            if not self.config.include_ms1 and group_key[0] == 1:
                continue
            
            if not self.config.include_ms2 and group_key[0] == 2:
                continue
        
            
            rt = group_df['rt'].values
            im = group_df['im'].values
            mz = group_df['mz'].values
            x_title, y_title, z_title = 'RT', 'IM', 'MZ'

            intensity = group_df['int'].values  # Assuming 'intensity' is the column representing intensity

            rt_grid, im_grid, mz_grid = np.meshgrid(rt, im, mz, indexing='ij')

            # Create a 3D surface plot for each group
            trace = go.Mesh3d(x=rt_grid, y=im_grid, z=mz_grid, opacity=0.5)
            row_num = math.floor(i / num_cols) + 1  # Calculate the row number based on the number of columns
            col_num = i % num_cols + 1  # Calculate the column number based on the number of columns
            subfig.add_trace(trace, row=row_num, col=col_num)  # Use the calculated row and column numbers
            
            scene = dict(aspectmode='manual',
                        aspectratio=dict(x=1, y=1, z=1),
                        camera=dict(eye=dict(x=1.25, y=1.25, z=1.25)),
                        xaxis_title = x_title,
                        yaxis_title = y_title,
                        zaxis_title = z_title)
            
            subfig.update_scenes(scene, row=row_num, col=col_num)

        # Update the layout of the overall figure
        subfig.update_layout(height=len(featureMap['Annotation'].unique()) * 800,
                            width=len(featureMap['Annotation'].unique()) * 800, showlegend=False)
        
        subfig.update_coloraxes(showscale=False)

        return subfig
    
    def show(self):
        """
        Show the plot.
        """
        px.init_notebook_mode()
        self.fig.show()
    
