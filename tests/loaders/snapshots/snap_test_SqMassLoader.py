# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 1'] = {
    '../test_data/xics/test_chrom_1.sqMass': [
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 818.476013183594 RightWidth: 847.557983398438 Area: 15781.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 843.921997070312 RightWidth: 916.620971679688 Area: 40030.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 1018.39001464844 RightWidth: 1058.38000488281 Area: 11879.0 Qvalue: 0.6191579512574589'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 1091.08996582031 RightWidth: 1131.06994628906 Area: 6869.0 Qvalue: 0.21848283341834926'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 625.831970214844 RightWidth: 651.276977539062 Area: 3311.0 Qvalue: 0.6196804823619941')
    ],
    '../test_data/xics/test_chrom_2.sqMass': [
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 1174.68994140625 RightWidth: 1189.22998046875 Area: 1187.0 Qvalue: 0.6252601620692566'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 865.742004394531 RightWidth: 898.453002929688 Area: 3968.0 Qvalue: 0.15503077334651527'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 898.453002929688 RightWidth: 949.336975097656 Area: 5058.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 1131.07995605469 RightWidth: 1171.06005859375 Area: 4338.0 Qvalue: 0.611900807501989'),
        GenericRepr('TransitionGroupFeature Apex: None LeftWidth: 1200.14001464844 RightWidth: 1225.58996582031 Area: 2150.0 Qvalue: 0.6209295471091476')
    ]
}

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 2'] = 0

snapshots['TestSqMassLoader::test_loadTransitionGroupFeaturesDf 1'] = GenericRepr('                                filename  leftBoundary  rightBoundary  areaIntensity    qvalue  consensusApex  consensusApexIntensity\n0  ../test_data/xics/test_chrom_1.sqMass    818.476013     847.557983        64494.0  0.000277        838.622                 15781.0\n1  ../test_data/xics/test_chrom_1.sqMass    843.921997     916.620972       230773.0  0.000277        864.324                 40030.0\n2  ../test_data/xics/test_chrom_1.sqMass   1018.390015    1058.380005        76219.0  0.619158       1035.830                 11879.0\n3  ../test_data/xics/test_chrom_1.sqMass   1091.089966    1131.069946        48427.0  0.218483       1111.350                  6869.0\n4  ../test_data/xics/test_chrom_1.sqMass    625.831970     651.276978        14772.0  0.619680        636.468                  3311.0\n5  ../test_data/xics/test_chrom_2.sqMass   1174.689941    1189.229980         3697.0  0.625260       1178.480                  1187.0\n6  ../test_data/xics/test_chrom_2.sqMass    865.742004     898.453003        16398.0  0.155031        890.432                  3968.0\n7  ../test_data/xics/test_chrom_2.sqMass    898.453003     949.336975        29383.0  0.000277        915.050                  5058.0\n8  ../test_data/xics/test_chrom_2.sqMass   1131.079956    1171.060059        22497.0  0.611901       1151.740                  4338.0\n9  ../test_data/xics/test_chrom_2.sqMass   1200.140015    1225.589966         7743.0  0.620930       1204.060                  2150.0')

snapshots['TestSqMassLoader::test_loadTransitionGroups 1'] = {
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_1.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>'),
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_2.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>')
}

snapshots['TestSqMassLoader::test_loadTransitionGroupsDf 1'] = GenericRepr('                                   filename      rt    intensity         annotation\n0     ../test_data/xics/test_chrom_1.sqMass   512.8  1069.051908  2274_Precursor_i0\n1     ../test_data/xics/test_chrom_1.sqMass   516.4  2230.982597  2274_Precursor_i0\n2     ../test_data/xics/test_chrom_1.sqMass   520.0  2583.056921  2274_Precursor_i0\n3     ../test_data/xics/test_chrom_1.sqMass   523.7  1876.955276  2274_Precursor_i0\n4     ../test_data/xics/test_chrom_1.sqMass   527.3  1862.126603  2274_Precursor_i0\n...                                     ...     ...          ...                ...\n2697  ../test_data/xics/test_chrom_2.sqMass  1251.0     0.000000               b4^1\n2698  ../test_data/xics/test_chrom_2.sqMass  1254.7    42.001872               b4^1\n2699  ../test_data/xics/test_chrom_2.sqMass  1258.3    20.999608               b4^1\n2700  ../test_data/xics/test_chrom_2.sqMass  1261.9    20.999608               b4^1\n2701  ../test_data/xics/test_chrom_2.sqMass  1265.6     0.000000               b4^1\n\n[2702 rows x 4 columns]')
