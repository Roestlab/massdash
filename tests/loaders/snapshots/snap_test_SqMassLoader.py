"""
tests/loaders/snapshots/snap_test_SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 1'] = {
    '../test_data/xics/test_chrom_1.sqMass': [
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 818.476013183594 RightWidth: 847.557983398438 Area: 15781.0 Qvalue: 0.07677153679402818'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 818.476013183594 RightWidth: 847.557983398438 Area: 15781.0 Qvalue: 0.491091881315617'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 843.921997070312 RightWidth: 916.620971679688 Area: 40030.0 Qvalue: 0.10215831770233398'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 843.921997070312 RightWidth: 916.620971679688 Area: 40030.0 Qvalue: 0.4342245125263835')
    ],
    '../test_data/xics/test_chrom_2.sqMass': [
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 898.453002929688 RightWidth: 949.336975097656 Area: 5058.0 Qvalue: 0.1626996593610084'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 898.453002929688 RightWidth: 949.336975097656 Area: 5058.0 Qvalue: 0.3294686614863428')
    ]
}

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 2'] = 2

snapshots['TestSqMassLoader::test_loadTransitionGroupFeaturesDf 1'] = GenericRepr('                                filename  leftBoundary  rightBoundary  areaIntensity    qvalue  consensusApex  consensusApexIntensity\n0  ../test_data/xics/test_chrom_1.sqMass    818.476013     847.557983        64494.0  0.000277        838.622                 15781.0\n1  ../test_data/xics/test_chrom_1.sqMass    818.476013     847.557983        64494.0  0.000277        838.622                 15781.0\n2  ../test_data/xics/test_chrom_1.sqMass    843.921997     916.620972       230773.0  0.000277        864.324                 40030.0\n3  ../test_data/xics/test_chrom_1.sqMass    843.921997     916.620972       230773.0  0.000277        864.324                 40030.0\n4  ../test_data/xics/test_chrom_2.sqMass    898.453003     949.336975        29383.0  0.000277        915.050                  5058.0\n5  ../test_data/xics/test_chrom_2.sqMass    898.453003     949.336975        29383.0  0.000277        915.050                  5058.0')

snapshots['TestSqMassLoader::test_loadTransitionGroups 1'] = {
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_1.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>'),
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_2.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>')
}

snapshots['TestSqMassLoader::test_loadTransitionGroupsDf 1'] = GenericRepr('                                   filename      rt    intensity         annotation\n0     ../test_data/xics/test_chrom_1.sqMass   512.8  1069.051908  2274_Precursor_i0\n1     ../test_data/xics/test_chrom_1.sqMass   516.4  2230.982597  2274_Precursor_i0\n2     ../test_data/xics/test_chrom_1.sqMass   520.0  2583.056921  2274_Precursor_i0\n3     ../test_data/xics/test_chrom_1.sqMass   523.7  1876.955276  2274_Precursor_i0\n4     ../test_data/xics/test_chrom_1.sqMass   527.3  1862.126603  2274_Precursor_i0\n...                                     ...     ...          ...                ...\n2697  ../test_data/xics/test_chrom_2.sqMass  1251.0     0.000000               b4^1\n2698  ../test_data/xics/test_chrom_2.sqMass  1254.7    42.001872               b4^1\n2699  ../test_data/xics/test_chrom_2.sqMass  1258.3    20.999608               b4^1\n2700  ../test_data/xics/test_chrom_2.sqMass  1261.9    20.999608               b4^1\n2701  ../test_data/xics/test_chrom_2.sqMass  1265.6     0.000000               b4^1\n\n[2702 rows x 4 columns]')
