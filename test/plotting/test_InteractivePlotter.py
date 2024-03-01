"""
test/plotting/test_InteractivePlotter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pytest
import numpy as np

from massdash.testing.BokehSnapshotExtension import BokehSnapshotExtension
from massdash.plotting import InteractivePlotter, PlotConfig
from massdash.structs.TransitionGroup import TransitionGroup, Chromatogram, Mobilogram, Spectrum, TransitionGroupFeature

@pytest.fixture
def snapshot_bokeh(snapshot):
    return snapshot.use_extension(BokehSnapshotExtension)

@pytest.fixture
def chromatogram():
    rt = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    intensity = np.array([10, 20, 30, 40, 50, 40, 30, 20, 10])
    return Chromatogram(rt, intensity, label='prec')

@pytest.fixture
def chromatogram2():
    rt = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    intensity = np.array([5, 10, 15, 20, 25, 20, 15, 10, 5])
    return Chromatogram(rt, intensity, label='b3^1')

@pytest.fixture
def mobilogram():
    im = np.array([0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03])
    intensity = np.array([10, 20, 30, 40, 50, 40, 30, 20, 10])
    return Mobilogram(im, intensity, label='b5^2')

@pytest.fixture
def mobilogram2():
    im = np.array([0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03])
    intensity = np.array([5, 10, 15, 20, 25, 20, 15, 10, 5])
    return Mobilogram(im, intensity, label='prec')

@pytest.fixture
def transition_group_im(mobilogram, mobilogram2):
    return TransitionGroup(precursorData=[mobilogram2], transitionData=[mobilogram])

@pytest.fixture
def spectrum():
    mz = np.array([99.9, 100, 100.01])
    intensity = np.array([10, 20, 30])
    return Spectrum(mz, intensity, label='b5^2')

@pytest.fixture
def spectrum2():
    mz = np.array([499.98, 500, 500.02])
    intensity = np.array([5, 10, 15])
    return Spectrum(mz, intensity, label='prec')

@pytest.fixture
def transition_group_spectra(spectrum, spectrum2):
    return TransitionGroup(precursorData=[spectrum2], transitionData=[spectrum])


@pytest.fixture
def feature_im():
    left, right, intens, q = 0.95, 1.03, 210, 0.003
    return TransitionGroupFeature(left, right, intens, q)

@pytest.fixture
def feature1():
    left, right, intens, q = 2, 7, 210, 0.003
    return TransitionGroupFeature(left, right, intens, q)

@pytest.fixture
def feature2():
    left, right, intens, q = 3, 6, 150, 0.0001
    return TransitionGroupFeature(left, right, intens, q)

@pytest.fixture
def featureIm():
    left, right, intens, q = 0.95, 1.03, 210, 0.003
    return TransitionGroupFeature(left, right, intens, q)

@pytest.fixture(params=[
    dict(include_ms1=True, include_ms2=False, title=None, subtitle=None, smoothing_type=dict(type='none'), scale_intensity=False),
    dict(include_ms1=False, include_ms2=True, title=None, subtitle=None, smoothing_type=dict(type='none'), scale_intensity=False),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='none'), scale_intensity=True),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='sgolay', sgolay_polynomial_order=3, sgolay_frame_length=5), scale_intensity=True),
    dict(include_ms1=True, include_ms2=True, title="Title", subtitle="Title", smoothing_type=dict(type='none', gaussian_sigma=2.0, gaussian_window=5), scale_intensity=True),
])
def plot_config(request):
    config = PlotConfig()
    config.update(request.param)
    return config

@pytest.fixture
def transition_group(chromatogram, chromatogram2):
    return TransitionGroup(precursorData=[chromatogram], transitionData=[chromatogram2])

def test_plot_chromatogram_default(transition_group, snapshot_bokeh):
    # Create an instance of InteractivePlotter
    plotter = InteractivePlotter(config=PlotConfig())

    # Call the plot_chromatogram method
    plot = plotter.plot_chromatogram(transition_group)

    assert snapshot_bokeh == plot

def test_plot_chromatogram(transition_group, feature1, feature2, plot_config, snapshot_bokeh):
    # Create an instance of InteractivePlotter
    plotter = InteractivePlotter(config=plot_config)

    # Call the plot_chromatogram method
    plot = plotter.plot_chromatogram(transition_group, [feature1, feature2])

    assert snapshot_bokeh == plot

def test_plot_mobilogram_default(transition_group_im, snapshot_bokeh):
    # Create an instance of InteractivePlotter
    plotter = InteractivePlotter(config=PlotConfig())

    # Call the plot_mobilogram method
    plot = plotter.plot_mobilogram(transition_group_im)

    assert snapshot_bokeh == plot

def test_plot_mobilogram(transition_group_im, feature_im, plot_config, snapshot_bokeh):

    # Create an instance of InteractivePlotter
    plotter = InteractivePlotter(config=plot_config)

    # Call the plot_mobilogram method
    # plot = plotter.plot_mobilogram(transition_group_im, [feature_im]) #TODO mobiologram features not supported
    plot = plotter.plot_mobilogram(transition_group_im)

    assert snapshot_bokeh == plot

# only test default, no smoothing with spectra
def test_plot_spectra_default(transition_group_spectra, snapshot_bokeh):

    # Create an instance of InteractivePlotter
    plotter = InteractivePlotter(config=PlotConfig())

    # Call the plot_spectra method
    plot = plotter.plot_spectra(transition_group_spectra)

    assert snapshot_bokeh == plot