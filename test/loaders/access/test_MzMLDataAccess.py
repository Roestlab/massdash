"""
test/loaders/access/test_MzMLDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
import pyopenms as po
import sys

import pytest
from massdash.loaders.access.MzMLDataAccess import MzMLDataAccess
from massdash.structs import TargetedDIAConfig, TransitionGroupFeature
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from massdash.testing.NumpySnapshotExtension import NumpySnapshotExtenstion
from massdash.util import find_git_directory

## Note: Cached is not tested

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def mzml_data_access():
    # resave the experiment for this specific os
    if sys.platform == 'win32':

        exp = po.MSExperiment()
        po.MzMLFile().load(os.path.join(TEST_PATH, 'test_data', 'mzml', 'ionMobilityTest.mzML'), exp)
        po.MzMLFile().store(os.path.join(TEST_PATH, 'test_data', 'mzml', 'ionMobilityTest_tmp.mzML'), exp)

        mzml_data_access = MzMLDataAccess(os.path.join(TEST_PATH, 'test_data', 'mzml', 'ionMobilityTest_tmp.mzML'), readOptions='ondisk')
        return mzml_data_access
    else:
        mzml_data_access = MzMLDataAccess(os.path.join(TEST_PATH, 'test_data', 'mzml', 'ionMobilityTest.mzML'), readOptions='ondisk')
        return mzml_data_access

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.fixture
def snapshot_numpy(snapshot):
    return snapshot.use_extension(NumpySnapshotExtenstion)

@pytest.fixture
def peptide_product_annotation_list():
    return np.array(["A", "B", "C", "D", "E"])

@pytest.fixture
def reference_mz_values():
    return np.array([100.0, 150.0, 200.0, 250.0, 300.0])

def test_load_data(mzml_data_access):
    mzml_data_access.load_data()
    assert mzml_data_access.exp is not None
    assert mzml_data_access.meta_data is not None

@pytest.mark.parametrize("mslevel", [[1, 2], [1], [2]])
def test_get_target_ms_level_indices(mzml_data_access, mslevel, snapshot):
    indices = mzml_data_access.get_target_ms_level_indices(mslevel)
    assert snapshot == indices 

def test_get_spectra_rt_list(mzml_data_access, snapshot):
    rt_list = mzml_data_access.get_spectra_rt_list()
    assert snapshot == rt_list

@pytest.mark.parametrize("spec_indice", [0])
def test_load_spectrum(mzml_data_access, spec_indice, snapshot_numpy):
    mz, intens, im = mzml_data_access.load_spectrum(spec_indice)
    assert snapshot_numpy == np.column_stack([mz, intens, im[0].get_data()]) # note IM not tested here

@pytest.mark.parametrize("spec_indice", [0])
def test_filter_single_spectrum(mzml_data_access, spec_indice, snapshot_numpy):
    product_mzs = [504.2664, 591.2984, 704.3825, 851.4509, 966.4779, 1065.5463]
    annotations = ['y4^1', 'y5^1', 'y6^1', 'y7^1', 'y8^1', 'y9^1'] 
    feature = TransitionGroupFeature(leftBoundary=6233, 
                                     rightBoundary=6247, 
                                     consensusApex=6240.41, 
                                     consensusApexIM=0.98, 
                                     sequence='AFVDFLSDEIK', 
                                     precursor_charge=2, 
                                     precursor_mz=642.3295,
                                     product_mz=product_mzs,
                                     product_annotations=annotations)

    config = TargetedDIAConfig()
    filtered_spectrum = mzml_data_access.filter_single_spectrum(spec_indice, feature, config)
    fda = filtered_spectrum.getFloatDataArrays()[0]
    im = fda.get_data()
    mz, intens = filtered_spectrum.get_peaks()
    peaks = np.column_stack([mz, intens, im])
    assert snapshot_numpy == peaks 

def test_reduce_spectra(mzml_data_access, snapshot_pandas): # also tests msExperimentToFeatureMap()
    product_mzs = [504.2664, 591.2984, 704.3825, 851.4509, 966.4779, 1065.5463]
    annotations = ['y4^1', 'y5^1', 'y6^1', 'y7^1', 'y8^1', 'y9^1'] 
    feature = TransitionGroupFeature(leftBoundary=6233, 
                                     rightBoundary=6247, 
                                     consensusApex=6240.41, 
                                     consensusApexIM=0.98, 
                                     sequence='AFVDFLSDEIK', 
                                     precursor_charge=2, 
                                     precursor_mz=642.3295,
                                     product_mz=product_mzs,
                                     product_annotations=annotations)
    config = TargetedDIAConfig()
    config.rt_window = 2
    feature_map = mzml_data_access.reduce_spectra(feature, config)
    assert snapshot_pandas == feature_map.feature_df

@pytest.mark.parametrize("mz,expected_annot", [(150.01, 'B'), (249.99, 'D')])
def test_find_closest_reference_mz(reference_mz_values, peptide_product_annotation_list, mz, expected_annot):
    closest_mz_annot = MzMLDataAccess._find_closest_reference_mz(mz, reference_mz_values, peptide_product_annotation_list)
    assert expected_annot == closest_mz_annot

@pytest.mark.parametrize("level,mz,expected_annot", [(1, 100, 'prec'), (2, 200.01, 'C'), (2, 299.89, 'E')])
def test_apply_mz_mapping(reference_mz_values, peptide_product_annotation_list, level, mz, expected_annot):
    row = pd.Series(dict(mz=mz, ms_level=level))
    result = MzMLDataAccess._apply_mz_mapping(row, reference_mz_values, peptide_product_annotation_list)
    assert expected_annot == result