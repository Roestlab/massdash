"""
test/loaders/test_GenericLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from typing import Dict
from pathlib import Path

import pandas as pd
import pytest
from syrupy.extensions.amber import AmberDataSerializer

from massdash.util import find_git_directory
from massdash.structs.TransitionGroup import TransitionGroup
from massdash.loaders.GenericLoader import GenericLoader

class DummyGenericLoader(GenericLoader):
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        return super().loadTopTransitionGroupFeatureDf(pep_id, charge)
    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        return super().loadTransitionGroups(pep_id, charge)
    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        return super().loadTransitionGroupFeaturesDf(pep_id, charge)

TEST_PATH = find_git_directory(Path(__file__).resolve()).parent / 'test' / 'test_data'

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