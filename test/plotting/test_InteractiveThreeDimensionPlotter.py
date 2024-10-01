"""
test/plotting/test_InteractiveThreeDimensionPlotter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import sys
import pytest
import pandas as pd

from massdash.testing import NumpySnapshotExtension, PlotlySnapshotExtension
from massdash.plotting import InteractiveThreeDimensionPlotter, PlotConfig
from massdash.structs import FeatureMap
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data'

@pytest.fixture
def snapshot_plotly(snapshot):
    return snapshot.use_extension(PlotlySnapshotExtension)

@pytest.fixture
def snapshot_numpy(snapshot):
    return snapshot.use_extension(NumpySnapshotExtension)

@pytest.fixture
def featureMap():
    df = pd.read_csv(TEST_PATH / 'featureMap' / 'ionMobilityTestFeatureDf.tsv', sep='\t')
    return FeatureMap(df, sequence='TEST', precursor_charge=2)

@pytest.mark.parametrize('include_ms1,include_ms2', [(True, True), (True, False), (False, True)])
def test_plot_3d_scatter(featureMap, include_ms1, include_ms2, snapshot_plotly):
    config_dict = dict(include_ms1=include_ms1, include_ms2=include_ms2)
    config = PlotConfig()
    config.update(config_dict)
    plotter = InteractiveThreeDimensionPlotter(config)
    fig = plotter.plot(featureMap)
    assert snapshot_plotly == fig

def test_plot_3d_vline(featureMap, snapshot_plotly):
    config = PlotConfig()
    plotter = InteractiveThreeDimensionPlotter(config)
    fig = plotter.plot(featureMap)
    assert snapshot_plotly == fig

@pytest.skipif(sys.platform == 'Darwin', reason="Plots slightly different on mac")
@pytest.mark.parametrize('include_ms1,include_ms2,smoothing_dict,type_of_comparison', [
    # no smoothing
    (True, True, dict(type='none'), 'retention time vs m/z'), 
    (True, False, dict(type='none'), 'retention time vs m/z'), 
    (False, True, dict(type='none'), 'retention time vs m/z'),
    # sgolay smoothing
    (True, True, dict(type='sgolay', sgolay_frame_length=5, sgolay_polynomial_order=3), 'retention time vs m/z'), 
    # other comparisons
    (True, True, dict(type='none'), "retention time vs ion mobility vs m/z"),
    (True, True, dict(type='none'), "retention time vs ion mobility"),
    (True, True, dict(type='none'), "ion mobility vs m/z")
    ])
def test_plot_individual_3d_surface(featureMap, include_ms1, include_ms2, smoothing_dict, type_of_comparison, snapshot_plotly):
    if sys.platform == 'win32' and type_of_comparison == "ion mobility vs m/z": # ion mobility vs m/z leads to slightly different plot on windows and mac
        pass
    else:
        config_dict = dict(include_ms1=include_ms1, include_ms2=include_ms2, smoothing_dict=smoothing_dict, type_of_comparison=type_of_comparison)
        config = PlotConfig()
        config.update(config_dict)
        plotter = InteractiveThreeDimensionPlotter(config)
        fig = plotter.plot_individual_3d_surface(featureMap)
        assert snapshot_plotly == fig

def test_plot_individual_3d_surface_error(featureMap):
    config_dict = dict(type_of_comparison='INVALID')
    config = PlotConfig()
    config.update(config_dict)
    plotter = InteractiveThreeDimensionPlotter(config)
    with pytest.raises(ValueError):
        plotter.plot_individual_3d_surface(featureMap)

'''
@pytest.mark.parametrize('include_ms1,include_ms2', [(True, True), (True, False), (False, True)])
def test_plot_individual_3d_mesh_cube(featureMap, include_ms1, include_ms2, snapshot_plotly):
    config = PlotConfig()
    plotter = InteractiveThreeDimensionPlotter(config)
    fig = plotter.plot_individual_3d_mesh_cube(featureMap)
    assert snapshot_plotly == fig
'''

@pytest.skipif(sys.platform == 'Darwin', reason="Plots slightly different on mac")
@pytest.mark.parametrize('type_of_3d_plot,aggregate_mslevels,include_ms1,include_ms2,type_of_comparison', [
    # Scatter not aggregated
    ('3D Scatter Plot', False, True, True, ''), 
    ('3D Scatter Plot', False, True, False, ''), 
    ('3D Scatter Plot', False, False, True, ''),
    # Scatter aggregated
    ('3D Scatter Plot', True, True, True, ''), 
    ('3D Scatter Plot', True, True, False, ''), 
    ('3D Scatter Plot', True, False, True, ''),
    # 3D Surface (aggregation always false)
    ('3D Surface Plot', False, True, False, 'retention time vs m/z'), 
    ('3D Surface Plot', False, False, True, 'retention time vs m/z'), 
    ('3D Surface Plot', False, True, True, 'retention time vs m/z'), 
    ('3D Surface Plot', False, True, True, "retention time vs ion mobility vs m/z"),
    ('3D Surface Plot', False, True, True, "ion mobility vs m/z"),
    ('3D Surface Plot', False, True, True, "retention time vs ion mobility"),
    # 3D Line
    ('3D Line Plot', False, True, True, ''),
    ('3D Line Plot', False, False, True, ''),
    ('3D Line Plot', False, True, False, '')
    ])
def test_plot(featureMap, type_of_3d_plot, aggregate_mslevels, include_ms1, include_ms2, type_of_comparison, snapshot_plotly):
    if sys.platform == 'win32' and type_of_comparison == "ion mobility vs m/z": # ion mobility vs m/z surface plot leads to slightly different plot on windows or mac
        pass
    else:
        config_dict = dict(type_of_3d_plot=type_of_3d_plot, aggregate_mslevels=aggregate_mslevels, include_ms1=include_ms1, include_ms2=include_ms2, type_of_comparison=type_of_comparison)
        config = PlotConfig()
        config.update(config_dict)
        plotter = InteractiveThreeDimensionPlotter(config)
        fig = plotter.plot(featureMap)
        assert snapshot_plotly == fig

@pytest.mark.parametrize('type_of_3d_plot,aggregate_mslevels,type_of_comparison', [
    ('INVALID', False, ''), # invalid type_of_3d_plot
    ('3D Surface Plot', False, 'INVALID'), # invalid type_of_comparison
    ('3D Surface Plot', True, 'retention time vs m/z') # invalid aggregation, cannot aggregate 3D surface plot
])
def test_plot_error(featureMap, type_of_3d_plot, aggregate_mslevels, type_of_comparison):
    config_dict = dict(type_of_3d_plot=type_of_3d_plot, aggregate_mslevels=aggregate_mslevels, type_of_comparison=type_of_comparison)
    config = PlotConfig()
    config.update(config_dict)
    plotter = InteractiveThreeDimensionPlotter(config)
    with pytest.raises(ValueError):
        plotter.plot(featureMap)