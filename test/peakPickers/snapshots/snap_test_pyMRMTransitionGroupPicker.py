# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 1'] = [
    GenericRepr('<massdash.structs.TransitionFeature.TransitionFeature object at 0x100000000>')
]

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 2'] = [
    GenericRepr('<massdash.structs.TransitionFeature.TransitionFeature object at 0x100000000>'),
    GenericRepr('<massdash.structs.TransitionFeature.TransitionFeature object at 0x100000000>')
]

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 3'] = [
]

snapshots['TestFindPeakBoundaries::test_perform_chromatogram_peak_picking_merged_peak_picking 1'] = [
    GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 10.0\nrightBoundary: 18.0\nareaIntensity: 50.0\nconsensusApex: None\nconsensusApexIntensity: 5.0\nqvalue: None\nconsensusApexIM: None\nprecursor_mz: None\nprecursor_charge: None\nproduct_annotations: None\nproduct_mz: None\nsequence: None')
]

snapshots['TestFindPeakBoundaries::test_perform_chromatogram_peak_picking_multiple_peaks 1'] = [
    GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 21.0\nrightBoundary: 29.0\nareaIntensity: 87.0\nconsensusApex: None\nconsensusApexIntensity: 25.0\nqvalue: None\nconsensusApexIM: None\nprecursor_mz: None\nprecursor_charge: None\nproduct_annotations: None\nproduct_mz: None\nsequence: None'),
    GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 4.0\nrightBoundary: 12.0\nareaIntensity: 25.0\nconsensusApex: None\nconsensusApexIntensity: 5.0\nqvalue: None\nconsensusApexIM: None\nprecursor_mz: None\nprecursor_charge: None\nproduct_annotations: None\nproduct_mz: None\nsequence: None')
]

snapshots['TestFindPeakBoundaries::test_perform_chromatogram_peak_picking_single_peak 1'] = [
    GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 10.0\nrightBoundary: 18.0\nareaIntensity: 25.0\nconsensusApex: None\nconsensusApexIntensity: 5.0\nqvalue: None\nconsensusApexIM: None\nprecursor_mz: None\nprecursor_charge: None\nproduct_annotations: None\nproduct_mz: None\nsequence: None')
]

snapshots['TestFindPeakBoundaries::test_resolve_level 1'] = [
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>')
]

snapshots['TestFindPeakBoundaries::test_resolve_level 2'] = [
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>')
]

snapshots['TestFindPeakBoundaries::test_resolve_level 3'] = [
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massdash.structs.Chromatogram.Chromatogram object at 0x100000000>')
]
