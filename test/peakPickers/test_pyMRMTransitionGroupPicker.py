"""
test/peakPickers/test_pyMRMTransitionGroupPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np
import pytest

from massdash.peakPickers import pyMRMTransitionGroupPicker
from massdash.structs import Chromatogram, TransitionGroup, TransitionFeature, TransitionGroupFeature
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture(params=['chrom_empty', 'chrom_single_peak', 'chrom_multiple_peaks'])
def chrom(request):
    return request.getfixturevalue(request.param)

@pytest.fixture
def chrom_empty():
    rt_arr_short = np.arange(1, 6)
    empty_intens = np.zeros(5)
    return Chromatogram(rt_arr_short, empty_intens)

@pytest.fixture
def chrom_single_peak():
    rt_arr = np.arange(1, 26)
    intens_single_peak = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                            2, 3, 4, 5, 4, 3, 2, 1, 0,
                            0, 0, 0, 0, 0, 0], dtype=np.float64)   
    return Chromatogram(rt_arr, intens_single_peak)

@pytest.fixture
def chrom_multiple_peaks():
    rt_arr_long = np.arange(1, 37)
    intens_multiple_peaks = np.array([0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                    2, 1, 0, 0, 0, 0, 0, 0, 0,
                    0, 1, 3, 9, 18, 25, 18, 9, 3,
                    1, 0, 0, 0, 0, 0, 0, 0], dtype=np.float64)
    return Chromatogram(rt_arr_long, intens_multiple_peaks)


@pytest.fixture
def pyPeakPicker():
    return pyMRMTransitionGroupPicker(sgolay_frame_length=11, sgolay_polynomial_order=3)

def test_find_peak_boundaries(pyPeakPicker, chrom, snapshot_pandas):
    output = pyPeakPicker.find_peak_boundaries(chrom)
    df = TransitionFeature.toPandasDf(output)
    assert snapshot_pandas == df

### Test pick ###
def test_perform_chromatogram_peak_picking_single_chrom(pyPeakPicker, chrom, snapshot_pandas):
    output = pyPeakPicker.pick(TransitionGroup([chrom], []))
    df = TransitionGroupFeature.toPandasDf(output)
    assert snapshot_pandas == df

def test_perform_chromatogram_peak_picking_multiple_chroms(pyPeakPicker, chrom_single_peak, snapshot_pandas):
    output = pyPeakPicker.pick(TransitionGroup([chrom_single_peak, chrom_single_peak], []))
    df = TransitionGroupFeature.toPandasDf(output)
    assert snapshot_pandas == df

### Test get Level ###
@pytest.mark.parametrize("level", ["ms1ms2", "ms2", "ms1"])
def test_resolve_level(chrom_single_peak, chrom_empty, chrom_multiple_peaks, level, snapshot_pandas):
    tg = TransitionGroup([chrom_single_peak, chrom_empty], [chrom_multiple_peaks]) 

    picker = pyMRMTransitionGroupPicker(level=level)
    output = picker._resolveLevel(tg) #outputs a list of chromatograms

    # convert list of chromatograms to pandas df for snapshot
    tg_tmp = TransitionGroup(output, []) 
    assert snapshot_pandas == tg_tmp.toPandasDf()