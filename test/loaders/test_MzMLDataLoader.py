"""
test/loaders/test_MzMLDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import pytest
import pandas as pd
import pyopenms as po

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
    c.im_window = None
    c.rt_window = 5
    return c

@pytest.fixture(scope='session')
def mzml_files():
    # resave the experiment using pyopenms so do not have indexing problems with the os.
    files = [Path('test_raw_1.mzML'), Path('test_raw_2.mzML')]
    filePaths = [ str(TEST_PATH / 'test_data' / 'example_dia' / 'raw' / f) for f in files ]
    for f in filePaths:
        exp = po.MSExperiment()
        po.MzMLFile().load(f, exp) 
        po.MzMLFile().store(f, exp)
    return filePaths


@pytest.fixture(params=['openswath', 'diann', 'combined'])
def mzml_data_loader(request, mzml_files):
    libFile = None
    print(mzml_files)

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

    return MzMLDataLoader(rsltsFile=rsltsFile, dataFiles=mzml_files, libraryFile=libFile, verbose=False, mode='module')

def test_init_error():
    # if library file is not provided, an error should be raised when only DIA-NN report files are supplied
    with pytest.raises(ValueError):
        MzMLDataLoader(rsltsFile=f"{TEST_PATH}/test_data/example_dia/diann/report/test_diann_report_combined.tsv", dataFiles=f'{TEST_PATH}/test_data/example_dia/raw/test_raw_1.mzML', libraryFile=None, verbose=False, mode='module')

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTopTransitionGroupFeatureDf(mzml_data_loader, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTopTransitionGroupFeatureDf(pep, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize('pep,charge,runNames', [('DYASIDAAPEER', 2, None), ('DYASIDAAPEER', 2, 'test_raw_1'), ('DYASIDAAPEER', 2, ['test_raw_1', 'test_raw_2'])])
def test_loadTransitionGroups(mzml_data_loader, config, pep, charge, runNames, snapshot_pandas):
    groups = mzml_data_loader.loadTransitionGroups(pep, charge, config, runNames=runNames)
    assert snapshot_pandas == groups.toPandasDf()

@pytest.mark.parametrize('pep,charge', [('DYASIDAAPEER', 2)])
def test_loadTransitionGroupsDf(mzml_data_loader, config, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTransitionGroupsDf(pep, charge, config)
    assert snapshot_pandas == df

@pytest.mark.parametrize('pep,charge,runNames', [('DYASIDAAPEER', 2, None), ('DYASIDAAPEER', 2, 'test_raw_1'), ('DYASIDAAPEER', 2, ['test_raw_1', 'test_raw_2'])])
def test_loadFeatureMaps(mzml_data_loader, config, pep, charge, runNames, snapshot_pandas):
    feature_maps = mzml_data_loader.loadFeatureMaps(pep, charge, config, runNames=runNames)
    
    # note: only checking data not metadata like peptide sequence, charge and filename
    assert snapshot_pandas == pd.concat([ f.feature_df for f in feature_maps.values()])