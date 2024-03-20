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

@pytest.fixture
def mzml_data_loader(request):
    if request.param == 'osw':
        rsltsFile = f'{TEST_PATH}/test_data/example_dia/openswath/osw/test.osw'

        dataFilesPrefix = f'{TEST_PATH}/test_data/example_dia/raw/'
        dataFiles = [f"{dataFilesPrefix}/test_raw_1.mzML", f"{dataFilesPrefix}/test_raw_2.mzML"]
        return MzMLDataLoader(rsltsFile=rsltsFile, dataFiles=dataFiles, rsltsFileType='OpenSWATH')


@pytest.mark.parametrize('mzml_data_loader,pep,charge', [('osw', 'AGAANIVPNSTGAAK', 2)], indirect=['mzml_data_loader'])
def test_loadTopTransitionGroupFeatureDf(mzml_data_loader, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTopTransitionGroupFeatureDf(pep, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize('mzml_data_loader,pep,charge', [('osw', 'AGAANIVPNSTGAAK', 2)], indirect=['mzml_data_loader'])
def test_loadTransitionGroupFeaturesDf(mzml_data_loader, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTransitionGroupFeaturesDf(pep, charge)
    assert snapshot_pandas == df

@pytest.mark.parametrize('mzml_data_loader,pep,charge', [('osw', 'AGAANIVPNSTGAAK', 2)], indirect=['mzml_data_loader'])
def test_loadTransitionGroups(mzml_data_loader, config, pep, charge, snapshot_pandas):
    groups = mzml_data_loader.loadTransitionGroups(pep, charge, config)
    assert snapshot_pandas == groups.toPandasDf()

@pytest.mark.parametrize('mzml_data_loader,pep,charge', [('osw', 'AGAANIVPNSTGAAK', 2)], indirect=['mzml_data_loader'])
def test_loadTransitionGroupsDf(mzml_data_loader, config, pep, charge, snapshot_pandas):
    df = mzml_data_loader.loadTransitionGroupsDf(pep, charge, config)
    assert snapshot_pandas == df

@pytest.mark.parametrize('mzml_data_loader,pep,charge', [('osw', 'AGAANIVPNSTGAAK', 2)], indirect=['mzml_data_loader'])
def test_loadFeatureMaps(mzml_data_loader, config, pep, charge, snapshot_pandas):
    feature_maps = mzml_data_loader.loadFeatureMaps(pep, charge, config)
    
    # note: only checking data not metadata like peptide sequence, charge and filename
    assert snapshot_pandas == pd.concat([ f.feature_df for f in feature_maps.values()])