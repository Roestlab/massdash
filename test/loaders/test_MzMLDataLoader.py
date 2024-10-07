"""
test/loaders/test_MzMLDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import pytest
import pandas as pd

from massdash.loaders import MzMLDataLoader
from massdash.structs import TargetedDIAConfig
from massdash.testing import PandasSnapshotExtension 
from massdash.util import find_git_directory

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtension)

@pytest.fixture
def config():
    c = TargetedDIAConfig()
    c.rt_window = 5
    return c

@pytest.fixture(params=['openswath', 'diann', 'combined'])
def mzml_data_loader(request):
    dataFilesPrefix = f'{TEST_PATH}/test_data/example_dia/raw/'
    dataFiles = [f"{dataFilesPrefix}/test_raw_1.mzML", f"{dataFilesPrefix}/test_raw_2.mzML"]
    libFile = None

    if request.param == 'openswath':
        rsltsFile = f'{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw'
    elif request.param == 'diann':
        rsltsFile = f'{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv'
        libFile = f'{TEST_PATH}/test_data/example_dia/diann/lib/test_1_lib.tsv'
    elif request.param == 'combined': # note: if two results files are specified, the first one will be used for extraction
        rsltsFile = [f'{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv', 
                     f'{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw']
    else:
        raise ValueError(f"Invalid parameter: {request.param}")

    return MzMLDataLoader(rsltsFile=rsltsFile, dataFiles=dataFiles, libraryFile=libFile, verbose=False, mode='module')

def test_init_error():
    # if library file is not provided, an error should be raised when only DIA-NN report files are supplied
    with pytest.raises(ValueError):
        MzMLDataLoader(rsltsFile=f"{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv", dataFiles=f'{TEST_PATH}/test_data/example_dia/raw/test_raw_1.mzML', libraryFile=None, verbose=False, mode='module')

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTopTransitionGroupFeatureDf(mzml_data_loader, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTopTransitionGroupFeatureDf(pep, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTransitionGroupFeaturesDf(mzml_data_loader, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTransitionGroupFeaturesDf(pep, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTransitionGroups(mzml_data_loader, config, pep, charge, snapshot_pandas):
    groups = mzml_data_loader.loadTransitionGroups(pep, charge, config)
    assert snapshot_pandas == groups.toPandasDf()

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTransitionGroupsDf(mzml_data_loader, config, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTransitionGroupsDf(pep, charge, config)
    assert snapshot_pandas == df

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadFeatureMaps(mzml_data_loader, config, pep, charge, snapshot_pandas):
    feature_maps = mzml_data_loader.loadFeatureMaps(pep, charge, config)
    
    # note: only checking data not metadata like peptide sequence, charge and filename
    assert snapshot_pandas == pd.concat([ f.feature_df for f in feature_maps.values()])