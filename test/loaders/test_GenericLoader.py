"""
test/loaders/test_GenericLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from typing import Dict
from massdash.structs.TransitionGroup import TransitionGroup
from pandas.core.api import DataFrame as DataFrame
import pytest
from massdash.loaders.GenericLoader import GenericLoader
from syrupy.extensions.amber import AmberDataSerializer

class DummyGenericLoader(GenericLoader):
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> DataFrame:
        return super().loadTopTransitionGroupFeatureDf(pep_id, charge)
    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        return super().loadTransitionGroups(pep_id, charge)
    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> DataFrame:
        return super().loadTransitionGroupFeaturesDf(pep_id, charge)

TEST_PATH = "../test_data/"

@pytest.fixture
def loader(request):
    if request.param == 'osw':
        return DummyGenericLoader(rsltsFile=os.path.join(TEST_PATH, 'osw', 'ionMobilityTest.osw'), dataFiles=[], rsltsFileType='OpenSWATH')
    if request.param == 'diann':
        return DummyGenericLoader(rsltsFile=os.path.join(TEST_PATH, 'diann', 'ionMobilityTest-diannReport.tsv'), 
                                  dataFiles=[], 
                                  libraryFile=os.path.join(TEST_PATH, 'library', 'ionMobilityTestLibrary.tsv'),
                                  rsltsFileType='DIA-NN')

@pytest.mark.parametrize("loader", ['osw', 'diann'], indirect=True)
def test_loadTransitionGroupFeatures(loader, snapshot):
    pep_id = 'AFVDFLSDEIK'
    charge = 2
    features = loader.loadTransitionGroupFeatures(pep_id, charge)
    assert snapshot == AmberDataSerializer.serialize(features)

@pytest.mark.parametrize("loader", ['osw', 'diann'], indirect=True)
def test_loadTopTransitionGroupFeature(loader, snapshot):
    pep_id = 'AFVDFLSDEIK'
    charge = 2
    top_feature = loader.loadTopTransitionGroupFeature(pep_id, charge)
    assert snapshot == AmberDataSerializer.serialize(top_feature)