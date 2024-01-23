# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 1'] = {
    '/Users/irahorecka/Desktop/Harddrive_Desktop/PhD/University of Toronto/Rost Lab/GitHub/massdash/test/test_data/xics/test_chrom_1.sqMass': [
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 818.476013183594\nrightBoundary: 847.557983398438\nareaIntensity: 64494.0\nconsensusApex: 838.622\nconsensusApexIntensity: 15781.0\nqvalue: 0.07677153679402818\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)'),
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 818.476013183594\nrightBoundary: 847.557983398438\nareaIntensity: 64494.0\nconsensusApex: 838.622\nconsensusApexIntensity: 15781.0\nqvalue: 0.491091881315617\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)'),
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 843.921997070312\nrightBoundary: 916.620971679688\nareaIntensity: 230773.0\nconsensusApex: 864.324\nconsensusApexIntensity: 40030.0\nqvalue: 0.10215831770233398\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)'),
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 843.921997070312\nrightBoundary: 916.620971679688\nareaIntensity: 230773.0\nconsensusApex: 864.324\nconsensusApexIntensity: 40030.0\nqvalue: 0.4342245125263835\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)')
    ],
    '/Users/irahorecka/Desktop/Harddrive_Desktop/PhD/University of Toronto/Rost Lab/GitHub/massdash/test/test_data/xics/test_chrom_2.sqMass': [
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 898.453002929688\nrightBoundary: 949.336975097656\nareaIntensity: 29383.0\nconsensusApex: 915.05\nconsensusApexIntensity: 5058.0\nqvalue: 0.1626996593610084\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)'),
        GenericRepr('-------- TransitionGroupFeature --------\nleftBoundary: 898.453002929688\nrightBoundary: 949.336975097656\nareaIntensity: 29383.0\nconsensusApex: 915.05\nconsensusApexIntensity: 5058.0\nqvalue: 0.3294686614863428\nconsensusApexIM: -1\nprecursor_mz: None\nprecursor_charge: 3\nproduct_annotations: None\nproduct_mz: None\nsequence: NKESPT(UniMod:21)KAIVR(UniMod:267)')
    ]
}

snapshots['TestSqMassLoader::test_loadTransitionGroupFeature 2'] = 2

snapshots['TestSqMassLoader::test_loadTransitionGroups 1'] = {
    GenericRepr('SqMassDataAccess(filename=/Users/irahorecka/Desktop/Harddrive_Desktop/PhD/University of Toronto/Rost Lab/GitHub/massdash/test/test_data/xics/test_chrom_1.sqMass)'): GenericRepr('<massdash.structs.TransitionGroup.TransitionGroup object at 0x100000000>'),
    GenericRepr('SqMassDataAccess(filename=/Users/irahorecka/Desktop/Harddrive_Desktop/PhD/University of Toronto/Rost Lab/GitHub/massdash/test/test_data/xics/test_chrom_2.sqMass)'): GenericRepr('<massdash.structs.TransitionGroup.TransitionGroup object at 0x100000000>')
}
