from pathlib import Path
import pytest
import numpy as np
import os
from typing import Literal

from massdash.peakPickers import ConformerPeakPicker
from massdash.loaders import SpectralLibraryLoader
from massdash.structs import TransitionGroup, TransitionGroupFeature, Chromatogram
from massdash.util import download_file, find_git_directory
from massdash.constants import URL_PRETRAINED_CONFORMER
from massdash.testing.NumpySnapshotExtension import NumpySnapshotExtenstion
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

class DummyConformerPeakPicker(ConformerPeakPicker):
   def __init__(self, library: SpectralLibraryLoader, pretrained_model_file: str, prediction_threshold: float = 0.5, prediction_type: Literal['logits', 'sigmoided', 'binarized'] = "logits"):
        self.pretrained_model_file = pretrained_model_file
        self.prediction_threshold = prediction_threshold
        self.prediction_type = prediction_type
        self.library = library
        
        ## set in load_model
        self.onnx_session = None
        self.window_size = None

@pytest.fixture
def snapshot_numpy(snapshot):
    return snapshot.use_extension(NumpySnapshotExtenstion)

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
                            0, 0, 0, 0, 0, 0])   
    return Chromatogram(rt_arr, intens_single_peak)

@pytest.fixture
def tg():
    rt_arr = np.arange(1, 26)
    intens_single_peak = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                            2, 3, 4, 5, 4, 3, 2, 1, 0,
                            0, 0, 0, 0, 0, 0])   
    ms1_chrom = Chromatogram(rt_arr, intens_single_peak, label="prec")
    ch1 = Chromatogram(rt_arr, intens_single_peak, label="b3^1")
    ch2 = Chromatogram(rt_arr, intens_single_peak, label="y10^1")
    ch3 = Chromatogram(rt_arr, intens_single_peak, label="y11^1")
    ch4 = Chromatogram(rt_arr, intens_single_peak, label="b6^1")
    ch5 = Chromatogram(rt_arr, intens_single_peak, label="b7^2")
    ch6 = Chromatogram(rt_arr, intens_single_peak, label="b5^1")

    return TransitionGroup([ms1_chrom], [ch1, ch2, ch3, ch4, ch5, ch6], precursor_charge=2, sequence='AGAANIVPNSTGAAK')


@pytest.fixture
def chrom_multiple_peaks():
    rt_arr_long = np.arange(1, 37)
    intens_multiple_peaks = np.array([0, 0, 0, 1, 2, 3, 4, 5, 4, 3,
                    2, 1, 0, 0, 0, 0, 0, 0, 0,
                    0, 1, 3, 9, 18, 25, 18, 9, 3,
                    1, 0, 0, 0, 0, 0, 0, 0])
    return Chromatogram(rt_arr_long, intens_multiple_peaks)

@pytest.fixture
def onnx_file():
    onnx_path_dir = f'{TEST_PATH}/test_data/'
    onnx_path = f'{onnx_path_dir}/base_cape.onnx'
    if not os.path.exists(onnx_path):
        download_file(URL_PRETRAINED_CONFORMER, onnx_path_dir)
    return onnx_path

@pytest.fixture
def lib():
    return SpectralLibraryLoader(f'{TEST_PATH}/test_data/example_dia/diann/lib/test_1_lib.tsv')

@pytest.fixture
def dummyPeakPicker(lib, onnx_file):
    return DummyConformerPeakPicker(lib, onnx_file)

@pytest.fixture
def dummyPeakPickerInvalid(lib):
    onnx_path = 'INVALID_PATH'
    return DummyConformerPeakPicker(lib, onnx_path)

@pytest.fixture
def peakPicker(lib, onnx_file):
    return ConformerPeakPicker(lib, onnx_file)

def test_validate_model(dummyPeakPicker):
    assert dummyPeakPicker._validate_model() == None

def test_validate_model_invalid(dummyPeakPickerInvalid):
    with pytest.raises(ValueError) as err:
        dummyPeakPickerInvalid._validate_model()

def test_load_model(peakPicker):
    peakPicker.load_model() 
    assert peakPicker.window_size == 175 # window size is automatically determined 

def test_preprocess(peakPicker, tg, snapshot_numpy):
    peakPicker.window_size = 25 # size of chromatograms is 25
    arr = peakPicker._preprocess(tg)

    # reshape array to 2d and then save 
    arr_2d = arr.reshape(-1, arr.shape[-1])
    assert snapshot_numpy == arr_2d
 
def test_convertConformerFeatureToTransitionGroupFeatures(peakPicker, snapshot_pandas):
    peak_info = {"peak1": [{"rt_apex": 10, "rt_start": 5, "rt_end": 15}]}
    max_int_transition = 1000
    features = peakPicker._convertConformerFeatureToTransitionGroupFeatures(peak_info, max_int_transition)
    assert isinstance(features, list)
    df = TransitionGroupFeature.toPandasDf(features)
    assert snapshot_pandas == df

def test_find_thresholds():
    # function not used
    pass

def test_find_top_peaks():
    pass

def test_get_peak_boundaries():
    pass

def test_pick(peakPicker, tg, snapshot_pandas):
    peakPicker.load_model()
    features = peakPicker.pick(tg)
    df = TransitionGroupFeature.toPandasDf(features)
    assert snapshot_pandas == df