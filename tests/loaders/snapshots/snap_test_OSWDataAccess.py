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

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfo 2'] = GenericRepr('     PEPTIDE_ID  PRECURSOR_ID  TRANSITION_ID UNMODIFIED_SEQUENCE                     MODIFIED_SEQUENCE  ...  PRODUCT_LIBRARY_INTENSITY  PRODUCT_DETECTING PEPTIDE_DECOY  PRECURSOR_DECOY  TRANSITION_DECOY\n0           207            29            174       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                    4600.67                  1             0                0                 0\n1           207            29            175       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                    1638.61                  1             0                0                 0\n2           207            29            176       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                    1329.33                  1             0                0                 0\n3           207            29            177       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                    1307.36                  1             0                0                 0\n4           207            29            178       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                    1250.76                  1             0                0                 0\n..          ...           ...            ...                 ...                                   ...  ...                        ...                ...           ...              ...               ...\n384         207            29         700416       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                      -1.00                  0             0                0                 1\n385         207            29         700417       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                      -1.00                  0             0                0                 1\n386         207            29         700418       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                      -1.00                  0             0                0                 1\n387         207            29         700419       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                      -1.00                  0             0                0                 1\n388         207            29         700420       ANSSPTTNIDHLK  ANS(UniMod:21)SPTTNIDHLK(UniMod:259)  ...                      -1.00                  0             0                0                 1\n\n[389 rows x 20 columns]')

snapshots['TestOSWDataAccess::test_getPeptideTransitionInfoShort 1'] = GenericRepr('TRANSITION_ID    [174, 175, 176, 177, 178, 179, 20295, 20296, 2...\nANNOTATION       [y9^1, y3^1, y7^1, y8^1, y4^1, y10^1, -1^1, b1...\nPRECURSOR_ID                                                    29\nName: (ANS(UniMod:21)SPTTNIDHLK(UniMod:259), 2), dtype: object')

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
