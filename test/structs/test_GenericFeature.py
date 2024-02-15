from massdash.structs.GenericFeature import GenericFeature
from typing import Tuple, Optional
import unittest

class DummyGenericFeature(GenericFeature):
    def __init__(self, leftBoundary: float, rightBoundary: float, areaIntensity: Optional[float] = None):
        super().__init__(leftBoundary, rightBoundary, areaIntensity)

    def getBoundaries(self) -> Tuple[float, float]:
        return (self.leftBoundary, self.rightBoundary)

class TestGenericFeature(unittest.TestCase):
    def test_get_boundaries(self):
        feature = DummyGenericFeature(0.0, 1.0)
        assert feature.getBoundaries() == (0.0, 1.0)

    def test_get_boundaries_with_area_intensity(self):
        feature = DummyGenericFeature(0.0, 1.0, areaIntensity=10.0)
        assert feature.getBoundaries() == (0.0, 1.0)

    def test_get_boundaries_with_negative_boundaries(self):
        feature = DummyGenericFeature(-1.0, -0.5)
        assert feature.getBoundaries() == (-1.0, -0.5)
