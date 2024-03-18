"""
test/structs/test_TransitionFeature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from massdash.structs.TransitionFeature import TransitionFeature
import pandas as pd

def test_TransitionFeature_init():
    # Test case 1: All parameters are None
    feature = TransitionFeature()
    assert feature.leftBoundary is None
    assert feature.rightBoundary is None
    assert feature.areaIntensity is None
    assert feature.peakApex is None
    assert feature.apexIntensity is None

    # Test case 2: Initialize with values
    feature = TransitionFeature(leftBoundary=0.5, rightBoundary=1.5, areaIntensity=10.0, peakApex=1.0, apexIntensity=5.0)
    assert feature.leftBoundary == 0.5
    assert feature.rightBoundary == 1.5
    assert feature.areaIntensity == 10.0
    assert feature.peakApex == 1.0
    assert feature.apexIntensity == 5.0

def test_TransitionFeature_getBoundaries_empty():
    # Test case 1: Boundaries are None
    feature = TransitionFeature()
    assert feature.getBoundaries() == (None, None)

    # Test case 2: Boundaries have values
    feature = TransitionFeature(leftBoundary=0.5, rightBoundary=1.5)
    assert feature.getBoundaries() == (0.5, 1.5)

def test_TransitionFeature_toPandasDf():
    # Test case 1: Empty list of TransitionFeature objects
    transitionFeatureLst = []
    df = TransitionFeature.toPandasDf(transitionFeatureLst)
    dfExpected = pd.DataFrame(columns=['leftBoundary', 'rightBoundary', 'areaIntensity', 'peakApex', 'apexIntensity'])
    pd.testing.assert_frame_equal(df, dfExpected, check_dtype=False)

    # Test case 2: List of TransitionFeature objects
    feature1 = TransitionFeature(leftBoundary=0.5, rightBoundary=1.5, areaIntensity=10.0, peakApex=1.0, apexIntensity=1.0)
    feature2 = TransitionFeature(leftBoundary=1.0, rightBoundary=2.0, areaIntensity=20.0, peakApex=1.5, apexIntensity=5.0)
    transitionFeatureLst = [feature1, feature2]
    df = TransitionFeature.toPandasDf(transitionFeatureLst)
    dfExpected = pd.DataFrame({'leftBoundary': [0.5, 1.0], 'rightBoundary': [1.5, 2.0], 'areaIntensity': [10, 20], 'peakApex': [1, 1.5], 'apexIntensity': [1, 5]})
    pd.testing.assert_frame_equal(df, dfExpected, check_dtype=False)