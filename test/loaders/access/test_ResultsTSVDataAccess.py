import pytest
from massdash.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from massdash.testing.PandasSnapshotExtension import PandasSnapshotExtenstion
from syrupy.extensions.amber import AmberDataSerializer


@pytest.fixture
def access(request):
    if request.param == 'diann':
        return ResultsTSVDataAccess("../../test_data/example_dia/diann/report/test_1_diann_report.tsv", 'DIA-NN')
    if request.param == 'dream':
        return ResultsTSVDataAccess("../../test_data/example_dia/dreamdia/test_dreamdia_report.tsv", 'DreamDIA')

@pytest.fixture
def runname():
    return 'test_raw_1'

@pytest.fixture
def peptide():
    return 'DYASIDAAPEER'

@pytest.fixture
def charge():
    return 2

@pytest.fixture
def snapshot_pandas(snapshot):
    return snapshot.use_extension(PandasSnapshotExtenstion)

@pytest.mark.parametrize("access", ['diann', 'dream'], indirect=True)
def test_loadData(access, snapshot_pandas):
    data = access.loadData()
    assert snapshot_pandas == data

@pytest.mark.parametrize("access", ['diann', 'dream'], indirect=True)
def test_initializePeptideHashTable(access, snapshot_pandas):
    hash_table = access._initializePeptideHashTable()
    assert snapshot_pandas == hash_table

#@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2), ('dream', 'test_raw_1', 'DYASIDAAPEER', 2)], indirect=['access'])
@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTopTransitionGroupFeature(access, runname, peptide, charge, snapshot):
    feature = access.getTopTransitionGroupFeature(runname, peptide, charge)
    assert snapshot == AmberDataSerializer.object_as_named_tuple(feature)

#@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2), ('dream', 'test_raw_1', 'DYASIDAAPEER', 2)], indirect=['access'])
@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTransitionGroupFeatures(access, runname, peptide, charge, snapshot):
    features = access.getTransitionGroupFeatures(runname, peptide, charge)
    assert snapshot == [ AmberDataSerializer.object_as_named_tuple(i) for i in features ]

#@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2), ('dream', 'test_raw_1', 'DYASIDAAPEER', 2)], indirect=['access'])
@pytest.mark.parametrize("access,runname,peptide,charge", [('diann', 'test_raw_1', 'DYASIDAAPEER', 2),], indirect=['access'])
def test_getTransitionGroupFeaturesDf(access, runname, peptide, charge, snapshot_pandas):
    df = access.getTransitionGroupFeaturesDf(runname, peptide, charge)
    assert snapshot_pandas == df