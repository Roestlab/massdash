"""
test/snapshots/test_snap_peak_picking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestCalculateHighestIntensity::test_calculate_highest_intensity_multiple_peaks 1'] = 5

snapshots['TestCalculateHighestIntensity::test_calculate_highest_intensity_single_peak 1'] = 5

snapshots['TestCalculateIntegratedIntensity::test_calculate_integrated_intensity_multiple_peaks 1'] = 25.0

snapshots['TestCalculateIntegratedIntensity::test_calculate_integrated_intensity_single_peak 1'] = 25.0

snapshots['TestCalculateMedianIntensity::test_calculate_median_intensity_multiple_peaks 1'] = 3.0

snapshots['TestCalculateMedianIntensity::test_calculate_median_intensity_single_peak 1'] = 3.0

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 1'] = {
    'ApexIntensity': GenericRepr('array([4.020979], dtype=float32)'),
    'ApexRT': GenericRepr('array([13.99999952])'),
    'FWHM': GenericRepr('array([6.40625], dtype=float32)'),
    'IntegratedIntensity': GenericRepr('array([25.], dtype=float32)'),
    'leftWidth': GenericRepr('array([10.], dtype=float32)'),
    'rightWidth': GenericRepr('array([18.], dtype=float32)')
}

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 2'] = {
    'ApexIntensity': GenericRepr('array([ 4.021002, 15.787879], dtype=float32)'),
    'ApexRT': GenericRepr('array([ 8.00791502, 24.99999952])'),
    'FWHM': GenericRepr('array([6.2301903, 5.8984375], dtype=float32)'),
    'IntegratedIntensity': GenericRepr('array([25., 87.], dtype=float32)'),
    'leftWidth': GenericRepr('array([ 4., 21.], dtype=float32)'),
    'rightWidth': GenericRepr('array([12., 29.], dtype=float32)')
}

snapshots['TestFindPeakBoundaries::test_find_peak_boundaries 3'] = None

snapshots['TestGetPeakBoundariesForSingleChromatogram::test_get_peak_boundaries_for_single_chromatogram_multiple_peaks 1'] = {
    'IntegratedIntensity': (
        25
    ,),
    'leftWidth': (
        GenericRepr('19.0')
    ,),
    'rightWidth': (
        GenericRepr('34.0')
    ,)
}

snapshots['TestGetPeakBoundariesForSingleChromatogram::test_get_peak_boundaries_for_single_chromatogram_no_peaks 1'] = None

snapshots['TestGetPeakBoundariesForSingleChromatogram::test_get_peak_boundaries_for_single_chromatogram_single_peak 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('11.0')
    ,),
    'rightWidth': (
        GenericRepr('18.0')
    ,)
}

snapshots['TestMergeAndCalculateConsensusPeakBoundaries::test_merge_and_calculate_consensus_peak_boundaries_multiple_chromatograms 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('11.0')
    ,),
    'rightWidth': (
        GenericRepr('20.0')
    ,)
}

snapshots['TestMergeAndCalculateConsensusPeakBoundaries::test_merge_and_calculate_consensus_peak_boundaries_single_chromatogram 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('11.0')
    ,),
    'rightWidth': (
        GenericRepr('18.0')
    ,)
}

snapshots['TestMergeAndCalculateConsensusPeakBoundaries::test_merge_and_calculate_consensus_peak_boundaries_top_n_features 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('11.0')
    ,),
    'rightWidth': (
        GenericRepr('20.0')
    ,)
}

snapshots['TestPerformChromatogramPeakPicking::test_perform_chromatogram_peak_picking_merged_peak_picking 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('10.0')
    ,),
    'rightWidth': (
        GenericRepr('19.0')
    ,)
}

snapshots['TestPerformChromatogramPeakPicking::test_perform_chromatogram_peak_picking_multiple_peaks 1'] = {
    'IntegratedIntensity': (
        25,
        5
    ),
    'leftWidth': (
        GenericRepr('21.0'),
        GenericRepr('4.0')
    ),
    'rightWidth': (
        GenericRepr('29.0'),
        GenericRepr('12.0')
    )
}

snapshots['TestPerformChromatogramPeakPicking::test_perform_chromatogram_peak_picking_single_peak 1'] = {
    'IntegratedIntensity': (
        5
    ,),
    'leftWidth': (
        GenericRepr('10.0')
    ,),
    'rightWidth': (
        GenericRepr('18.0')
    ,)
}
