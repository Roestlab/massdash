# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 1'] = {
    '../test_data/xics/test_chrom_1.sqMass': [
        GenericRepr('PeakFeature Apex: None LeftWidth: 818.476013183594 RightWidth: 847.557983398438 Area: 15781.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 843.921997070312 RightWidth: 916.620971679688 Area: 40030.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 1018.39001464844 RightWidth: 1058.38000488281 Area: 11879.0 Qvalue: 0.6191579512574589'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 1091.08996582031 RightWidth: 1131.06994628906 Area: 6869.0 Qvalue: 0.21848283341834926'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 625.831970214844 RightWidth: 651.276977539062 Area: 3311.0 Qvalue: 0.6196804823619941')
    ],
    '../test_data/xics/test_chrom_2.sqMass': [
        GenericRepr('PeakFeature Apex: None LeftWidth: 1174.68994140625 RightWidth: 1189.22998046875 Area: 1187.0 Qvalue: 0.6252601620692566'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 865.742004394531 RightWidth: 898.453002929688 Area: 3968.0 Qvalue: 0.15503077334651527'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 898.453002929688 RightWidth: 949.336975097656 Area: 5058.0 Qvalue: 0.00027720520546038556'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 1131.07995605469 RightWidth: 1171.06005859375 Area: 4338.0 Qvalue: 0.611900807501989'),
        GenericRepr('PeakFeature Apex: None LeftWidth: 1200.14001464844 RightWidth: 1225.58996582031 Area: 2150.0 Qvalue: 0.6209295471091476')
    ]
}

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 2'] = 0

snapshots['TestSqMassLoader::test_loadTransitionGroups 1'] = {
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_1.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>'),
    GenericRepr('SqMassDataAccess(filename=../test_data/xics/test_chrom_2.sqMass)'): GenericRepr('<massseer.structs.TransitionGroup.TransitionGroup object at 0x100000000>')
}
