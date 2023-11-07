# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSqMassDataAccess::test_getDataForChromatograms 1'] = 3

snapshots['TestSqMassDataAccess::test_getDataForChromatogramsFromNativeIds 1'] = 5

snapshots['TestSqMassDataAccess::test_getPrecursorChromIDs 1'] = [
    424
]
