# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['TestOSWDataAccess::test_getPeptideTable 1'] = (
    8,
    4
)

snapshots['TestOSWDataAccess::test_getPeptideTable 2'] = GenericRepr('     ID UNMODIFIED_SEQUENCE                     MODIFIED_SEQUENCE  DECOY\n0   207       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)      0\n1   207       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)      0\n2   218       ANSSPTTNIDHLK  ANSS(UniMod:21)PTTNIDHLK(UniMod:259)      0\n3   218       ANSSPTTNIDHLK  ANSS(UniMod:21)PTTNIDHLK(UniMod:259)      0\n4   220       ANSSPTTNIDHLK  ANSSPT(UniMod:21)TNIDHLK(UniMod:259)      0\n5  4707         NKESPTKAIVR    NKES(UniMod:21)PTKAIVR(UniMod:267)      0\n6  4707         NKESPTKAIVR    NKES(UniMod:21)PTKAIVR(UniMod:267)      0\n7  4709         NKESPTKAIVR    NKESPT(UniMod:21)KAIVR(UniMod:267)      0')

snapshots['TestOSWDataAccess::test_getPeptideTableFromProteinID 1'] = (
    5,
    4
)

snapshots['TestOSWDataAccess::test_getPeptideTableFromProteinID 2'] = GenericRepr('    ID UNMODIFIED_SEQUENCE                     MODIFIED_SEQUENCE  DECOY\n0  207       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)      0\n1  207       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)      0\n2  218       ANSSPTTNIDHLK  ANSS(UniMod:21)PTTNIDHLK(UniMod:259)      0\n3  218       ANSSPTTNIDHLK  ANSS(UniMod:21)PTTNIDHLK(UniMod:259)      0\n4  220       ANSSPTTNIDHLK  ANSSPT(UniMod:21)TNIDHLK(UniMod:259)      0')

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfo 1'] = (
    389,
    20
)

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfo 2'] = GenericRepr('     PEPTIDE_ID  PRECURSOR_ID  TRANSITION_ID UNMODIFIED_SEQUENCE  ... PRODUCT_DETECTING  PEPTIDE_DECOY  PRECURSOR_DECOY TRANSITION_DECOY\n0           207            29            174       ANSSPTTNIDHLK  ...                 1              0                0                0\n1           207            29            175       ANSSPTTNIDHLK  ...                 1              0                0                0\n2           207            29            176       ANSSPTTNIDHLK  ...                 1              0                0                0\n3           207            29            177       ANSSPTTNIDHLK  ...                 1              0                0                0\n4           207            29            178       ANSSPTTNIDHLK  ...                 1              0                0                0\n..          ...           ...            ...                 ...  ...               ...            ...              ...              ...\n384         207            29         700416       ANSSPTTNIDHLK  ...                 0              0                0                1\n385         207            29         700417       ANSSPTTNIDHLK  ...                 0              0                0                1\n386         207            29         700418       ANSSPTTNIDHLK  ...                 0              0                0                1\n387         207            29         700419       ANSSPTTNIDHLK  ...                 0              0                0                1\n388         207            29         700420       ANSSPTTNIDHLK  ...                 0              0                0                1\n\n[389 rows x 20 columns]')

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfoShort 1'] = (
    6,
    4
)

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfoShort 2'] = GenericRepr('   PRECURSOR_ID  TRANSITION_ID  PRECURSOR_CHARGE ANNOTATION\n0            29            174                 2       y9^1\n1            29            175                 2       y3^1\n2            29            176                 2       y7^1\n3            29            177                 2       y8^1\n4            29            178                 2       y4^1\n5            29            179                 2      y10^1')

snapshots['TestOSWDataAccess::test_getPrecursorCharges 1'] = (
    2,
    1
)

snapshots['TestOSWDataAccess::test_getPrecursorCharges 2'] = GenericRepr('   CHARGE\n0       2\n1       3')

snapshots['TestOSWDataAccess::test_getProteinTable 1'] = (
    5,
    4
)

snapshots['TestOSWDataAccess::test_getProteinTable 2'] = GenericRepr('   PROTEIN_ID  PEPTIDE_ID                 PROTEIN_ACCESSION  DECOY\n0         539         207  QQSVKANSSPTTNIDHLK;ANSSPTTNIDHLK      0\n1         539         218  QQSVKANSSPTTNIDHLK;ANSSPTTNIDHLK      0\n2         539         220  QQSVKANSSPTTNIDHLK;ANSSPTTNIDHLK      0\n3         507        4707                       NKESPTKAIVR      0\n4         507        4709                       NKESPTKAIVR      0')
