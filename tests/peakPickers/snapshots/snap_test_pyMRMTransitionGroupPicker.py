"""
tests/peakPickers/snapshots/snap_test_pyMRMTransitionGroupPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

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
    GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 10.0 RightWidth: 18.0 Area: 50.0 Qvalue: None')
]

snapshots['TestFindPeakBoundaries::test_perform_chromatogram_peak_picking_multiple_peaks 1'] = [
    GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 21.0 RightWidth: 29.0 Area: 87.0 Qvalue: None'),
    GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 4.0 RightWidth: 12.0 Area: 25.0 Qvalue: None')
]

snapshots['TestFindPeakBoundaries::test_perform_chromatogram_peak_picking_single_peak 1'] = [
    GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 10.0 RightWidth: 18.0 Area: 25.0 Qvalue: None')
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
