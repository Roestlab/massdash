"""
tests/loaders/snapshots/snap_test_SqMassDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestSqMassDataAccess::test_getDataForChromatograms 1'] = 3

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsDf 1'] = GenericRepr('         rt    intensity annotation\n0     513.2     0.000000       y4^1\n1     516.8     0.000000       y4^1\n2     520.4     0.000000       y4^1\n3     524.1     0.000000       y4^1\n4     527.7     0.000000       y4^1\n..      ...          ...        ...\n188  1196.5  4307.219175       y6^1\n189  1200.1  2296.903045       y6^1\n190  1203.8  1681.940417       y6^1\n191  1207.4  1562.995997       y6^1\n192  1211.0  2206.868643       y6^1\n\n[578 rows x 3 columns]')

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsDf 2'] = GenericRepr('Empty DataFrame\nColumns: [rt, intensity, annotation]\nIndex: []')

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsDf 3'] = GenericRepr('Empty DataFrame\nColumns: [rt, intensity, annotation]\nIndex: []')

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsFromNativeIds 1'] = 5

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsFromNativeIds 2'] = [
    GenericRepr('<massseer.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massseer.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massseer.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massseer.structs.Chromatogram.Chromatogram object at 0x100000000>'),
    GenericRepr('<massseer.structs.Chromatogram.Chromatogram object at 0x100000000>')
]

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsFromNativeIdsDf 1'] = GenericRepr('         rt   intensity annotation\n0    1454.9   62.999251       y4^1\n1    1458.6  105.000825       y4^1\n2    1462.2   84.002376       y4^1\n3    1465.8  166.992557       y4^1\n4    1469.5  272.996798       y4^1\n..      ...         ...        ...\n188  2138.3   62.998062       y7^1\n189  2141.9   83.999054       y7^1\n190  2145.6   83.999054       y7^1\n191  2149.2  210.005839       y7^1\n192  2152.8  104.999710       y7^1\n\n[965 rows x 3 columns]')

snapshots['TestSqMassDataAccess::test_getPrecursorChromIDs 1'] = [
    424
]
