"""
test/loaders/test_SpectralLibraryLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path
import pytest

from syrupy.extensions.amber import AmberDataSerializer
from massdash.structs import TransitionGroupFeature
from massdash.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massdash.util import find_git_directory
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test'

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)


@pytest.fixture
def spectral_library_loader(request):
    if request.param == 'diann':
        return SpectralLibraryLoader(f"{TEST_PATH}/test_data/example_dia/diann/lib/test_1_lib.tsv")
    if request.param == 'openswath':
        return SpectralLibraryLoader(f"{TEST_PATH}/test_data/example_dia/openswath/lib/test.pqp")
    if request.param == 'diann-im':
        return SpectralLibraryLoader(f'{TEST_PATH}/test_data/library/ionMobilityTestLibrary.tsv')

@pytest.fixture
def transition_group_features():
    return [TransitionGroupFeature(sequence="DYASIDAAPEER", precursor_charge=2, leftBoundary=10, rightBoundary=20)] # note left and right boundary not used so just dummy values

@pytest.mark.parametrize('spectral_library_loader', ['diann', 'openswath'], indirect=['spectral_library_loader'])
def test_load(spectral_library_loader, snapshot_pandas):
    data = spectral_library_loader.load()
    assert snapshot_pandas == data

def test_save():
    pass # not testable


@pytest.mark.parametrize('spectral_library_loader', ['diann', 'openswath'], indirect=['spectral_library_loader'])
def test_get_unique_proteins(spectral_library_loader, snapshot):
    proteins = spectral_library_loader.get_unique_proteins()
    assert snapshot == proteins


@pytest.mark.parametrize('spectral_library_loader', ['diann', 'openswath'], indirect=['spectral_library_loader'])
def test_get_unique_peptides_per_protein(spectral_library_loader, snapshot):
    peptides = spectral_library_loader.get_unique_peptides_per_protein("protein_name")
    assert snapshot == peptides


@pytest.mark.parametrize('spectral_library_loader', ['diann', 'openswath'], indirect=['spectral_library_loader'])
def test_get_unique_charge_states_per_peptide(spectral_library_loader, snapshot):
    charge_states = spectral_library_loader.get_unique_charge_states_per_peptide("peptide_sequence")
    assert snapshot == charge_states


@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_precursor_mz(spectral_library_loader, pep, charge, snapshot):
    precursor_mz = spectral_library_loader.get_peptide_precursor_mz(pep, charge)
    assert snapshot == precursor_mz


@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_product_mz_list(spectral_library_loader, pep, charge, snapshot):
    product_mz_list = spectral_library_loader.get_peptide_product_mz_list(pep, charge)
    assert snapshot == product_mz_list

def test_populateTransitionGroupFeature():
    pass # not used so not tested

@pytest.mark.parametrize('spectral_library_loader', ['diann', 'openswath'], indirect=['spectral_library_loader'])
def test_populateTransitionGroupFeatures(spectral_library_loader, transition_group_features, snapshot):
    features = spectral_library_loader.populateTransitionGroupFeatures(transition_group_features)
    assert snapshot == AmberDataSerializer.object_as_named_tuple(features)

@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_product_charge_list(spectral_library_loader, pep, charge, snapshot):
    product_charge_list = spectral_library_loader.get_peptide_product_charge_list(pep, charge)
    assert snapshot == product_charge_list


# note: does not work with DIA-NN since no NormalizedRetentionTime column
@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_retention_time(spectral_library_loader, pep, charge, snapshot):
    retention_time = spectral_library_loader.get_peptide_retention_time(pep, charge)
    assert snapshot == retention_time


@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann-im','AFVDFLSDEIK', 2), ], indirect=['spectral_library_loader'])
def test_get_peptide_ion_mobility(spectral_library_loader, pep, charge, snapshot):
    ion_mobility = spectral_library_loader.get_peptide_ion_mobility(pep, charge)
    assert snapshot == ion_mobility


@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_library_intensity(spectral_library_loader, pep, charge, snapshot):
    library_intensity = spectral_library_loader.get_peptide_library_intensity(pep, charge)
    assert snapshot == library_intensity


@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def test_get_peptide_fragment_annotation_list(spectral_library_loader, pep, charge, snapshot):
    fragment_annotation_list = spectral_library_loader.get_peptide_fragment_annotation_list(pep, charge)
    assert snapshot == fragment_annotation_list


@pytest.mark.parametrize('spectral_library_loader,pep,charge,fragment', [('diann','DYASIDAAPEER', 2, 'b3^1'), ('openswath', 'DYASIDAAPEER', 2, 'y4/0.01y10^2/0.50')], indirect=['spectral_library_loader'])
def test_get_fragment_library_intensity(spectral_library_loader, pep, charge, fragment, snapshot):
    library_intensity = spectral_library_loader.get_fragment_library_intensity(pep, charge, fragment)
    assert snapshot == library_intensity

@pytest.mark.parametrize('spectral_library_loader,pep,charge', [('diann','DYASIDAAPEER', 2), ('openswath', 'DYASIDAAPEER', 2)], indirect=['spectral_library_loader'])
def filter_for_target_transition_list(spectral_library_loader, pep, charge, target_transition_list, snapshot_pandas):
    filtered_transition_list = spectral_library_loader.filter_for_target_transition_list(pep, charge, target_transition_list)
    assert snapshot_pandas == filtered_transition_list