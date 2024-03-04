from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from bokeh.models import CrosshairTool


from massdash.testing.NumpySnapshotExtension import NumpySnapshotExtenstion
from massdash.testing.BokehSnapshotExtension import BokehSnapshotExtension
from massdash.plotting.InteractiveTwoDimensionPlotter import InteractiveTwoDimensionPlotter
from massdash.structs.FeatureMap import FeatureMap
from massdash.plotting.GenericPlotter import PlotConfig
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data'

@pytest.fixture
def snapshot_bokeh(snapshot):
    return snapshot.use_extension(BokehSnapshotExtension)

@pytest.fixture
def snapshot_numpy(snapshot):
    return snapshot.use_extension(NumpySnapshotExtenstion)

@pytest.fixture
def featureMap():
    df = pd.read_csv(TEST_PATH / 'featureMap' / 'ionMobilityTestFeatureDf.tsv', sep='\t')
    return FeatureMap(df, sequence='TEST', precursor_charge=2)

'''
@pytest.fixture(params=[
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Subtitle", smoothing_type=dict(type='none'), type_of_heatmap='m/z vs retention time'),
    dict(include_ms1=True, include_ms2=False, title=None, subtitle=None, smoothing_type=dict(type='none'), type_of_heatmap='m/z vs ion mobility'),
    dict(include_ms1=True, include_ms2=False, title=None, subtitle=None, smoothing_type=dict(type='none'), type_of_heatmap='m/z vs ion mobility'),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='none'), scale_intensity=True),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='sgolay', sgolay_polynomial_order=3, sgolay_frame_length=5), scale_intensity=True),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='gauss', gaussian_sigma=2.0, gaussian_window=5), scale_intensity=True),
])
def genericPlotter(request):
    config_dict = dict(include_ms1=True, 
                       include_ms2=True, 
                       title="Title", 
                       subtitle="Subtitle", 
                       type_of_heatmap='retention time vs ion mobility')
    config = PlotConfig()
    config.update(request.param)
    return InteractiveTwoDimensionPlotter(plot_config=config)
'''

@pytest.fixture
def defaultPlotter():
    config = PlotConfig()
    return InteractiveTwoDimensionPlotter(config)

@pytest.mark.parametrize('heatmap,expected1,expected2', 
                         [('m/z vs retention time', 'Retention time (s)', 'm/z'), 
                          ('m/z vs ion mobility', 'Ion mobility (1/K0)', 'm/z'), 
                          ('retention time vs ion mobility', 'Retention time (s)', 'Ion mobility (1/K0)')])
def test_get_axis_titles(heatmap, expected1, expected2):
    config = PlotConfig()
    config.update(dict(type_of_heatmap=heatmap))
    plotter = InteractiveTwoDimensionPlotter(config)
    axis1, axis2 = plotter.get_axis_titles()
    assert axis1 == expected1
    assert axis2 == expected2
    
@pytest.mark.parametrize('index,columns', [('mz', 'rt'), ('mz', 'im'), ('im', 'rt')])
def test_get_plot_parameters(defaultPlotter, index, columns, featureMap, snapshot_numpy):
    arr = featureMap.feature_df.pivot_table(index=index, columns=columns, values='int', aggfunc="sum")
    expected_output = np.concatenate([np.array([i]) if isinstance(i, float) else i for i in defaultPlotter.get_plot_parameters(arr) ])

    assert snapshot_numpy == expected_output

@pytest.mark.parametrize('index,columns,smoothing_dict,normalization_dict', [
    # mz vs rt
    ('mz', 'rt', dict(type='none'), dict(type='none')),
    ('mz', 'rt', dict(type='gauss', sigma=1.2), dict(type='none')),
    ('mz', 'rt', dict(type='none'), dict(type='equalization', bins=2)),
    ('mz', 'rt', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    ('mz', 'im', dict(type='none'), dict(type='none')),
    ('mz', 'im', dict(type='gauss', sigma=1.2), dict(type='none')),
    ('mz', 'im', dict(type='none'), dict(type='equalization', bins=2)),
    ('mz', 'im', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    ('im', 'rt', dict(type='none'), dict(type='none')),
    ('im', 'rt', dict(type='gauss', sigma=1.2), dict(type='none')),
    ('im', 'rt', dict(type='none'), dict(type='equalization', bins=2)),
    ('im', 'rt', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2))])
def test_prepare_array(featureMap, index, columns, smoothing_dict, normalization_dict, snapshot_numpy):
    arr = featureMap.feature_df.pivot_table(index=index, columns=columns, values='int', aggfunc="sum")
    config = PlotConfig()
    config.update(dict(smoothing_dict=smoothing_dict, normalization_dict=normalization_dict, include_ms1=True, include_ms2=True))
    plotter = InteractiveTwoDimensionPlotter(config)
    output = np.array(plotter.prepare_array(arr))
    assert snapshot_numpy == output


def test_create_heatmap_plot(featureMap, defaultPlotter, snapshot_bokeh):
    arr = featureMap.feature_df.pivot_table(index='im', columns='rt', values='int', aggfunc="sum")

    im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max = defaultPlotter.get_plot_parameters(arr) # TODO fill in manually do not rely on function
    linked_crosshair = CrosshairTool(dimensions="both")

    arr = arr.to_numpy()
    arr[np.isnan(arr)] = 0

    plot = defaultPlotter.create_heatmap_plot('title', arr, rt_min, rt_max, im_min, im_max, dw_main, dh_main, linked_crosshair, [])
    assert snapshot_bokeh == plot

@pytest.mark.parametrize('include_ms1,include_ms2,heatmap,smoothing_dict,normalization_dict', [
    ## include ms1 and ms2
    # mz vs rt
    (True, True, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (True, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (True, True, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (True, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (True, True, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (True, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),

    ## Only MS1
    # mz vs rt
    (True, False, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (True, False, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (True, False, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (True, False, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (True, False, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (True, False, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),

    ## Only MS2
    # mz vs rt
    (False, True, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (False, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (False, True, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (False, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (False, True, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (False, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2))])
def test_plot_aggregated_heatmap(defaultPlotter, featureMap, include_ms1, include_ms2, heatmap, smoothing_dict, normalization_dict, snapshot_bokeh):
    config = PlotConfig()
    config.update(dict(smoothing_dict=smoothing_dict, normalization_dict=normalization_dict, include_ms1=include_ms1, include_ms2=include_ms2, type_of_heatmap=heatmap))
    plot = defaultPlotter.plot_aggregated_heatmap(featureMap)
    assert snapshot_bokeh == plot


@pytest.mark.parametrize('include_ms1,include_ms2,heatmap,smoothing_dict,normalization_dict', [
## include ms1 and ms2
    # mz vs rt
    (True, True, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (True, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (True, True, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (True, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (True, True, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (True, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, True, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),

    ## Only MS1
    # mz vs rt
    (True, False, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (True, False, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (True, False, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (True, False, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (True, False, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (True, False, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (True, False, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (True, False, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),

    ## Only MS2
    # mz vs rt
    (False, True, 'm/z vs retention time', dict(type='none'), dict(type='none')),
    (False, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'm/z vs retention time', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'm/z vs retention time', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # mz vs im
    (False, True, 'm/z vs ion mobility', dict(type='none'), dict(type='none')),
    (False, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'm/z vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'm/z vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2)),
    # im vs rt
    (False, True, 'retention time vs ion mobility', dict(type='none'), dict(type='none')),
    (False, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='none')),
    (False, True, 'retention time vs ion mobility', dict(type='none'), dict(type='equalization', bins=2)),
    (False, True, 'retention time vs ion mobility', dict(type='gauss', sigma=1.2), dict(type='equalization', bins=2))])
def test_plot_individual_heatmaps(featureMap, include_ms1, include_ms2, heatmap, smoothing_dict, normalization_dict, snapshot, snapshot_bokeh):
    config = PlotConfig()
    config.update(dict(include_ms1=include_ms1, include_ms2=include_ms2, smoothing_type=smoothing_dict, normalization_dict=normalization_dict, type_of_heatmap=heatmap, title="Title", subtitle="Subtitle"))
    plotter = InteractiveTwoDimensionPlotter(config)
    plots = plotter.plot_individual_heatmaps(featureMap)
    assert len(plots) == snapshot
    assert snapshot_bokeh == plots[0] # only check the first plot, checking list of plots not supported