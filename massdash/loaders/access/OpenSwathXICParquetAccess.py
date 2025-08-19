"""
massdash/loaders/access/OpenSwathXICParquetAccess.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List
from collections import OrderedDict
import pyopenms as po
import sqlite3
import pandas as pd
import base64
import struct
import zlib
from pathlib import Path
import pyarrow.compute as pc
import pyarrow.dataset as ds

# Structs
from ...structs.Chromatogram import Chromatogram
# Utils

class OpenSwathXICParquetAccess:

    def __init__(self, filename):
        self.filename = filename
        self.runName = str(Path(filename).stem)
        self.parquet = ds.dataset(filename)

    def getChromatogramsFromSequenceAndCharge(self, sequence: str, charge: int):
        """
        Get chromatograms for a given peptide sequence and charge
        """
        df = self.parquet.scanner(
            columns=['RT_DATA', 'INTENSITY_DATA', 'RT_COMPRESSION', 'INTENSITY_COMPRESSION', 'TRANSITION_ORDINAL', 'TRANSITION_TYPE', 'PRODUCT_CHARGE', 'NATIVE_ID'],
            filter=( 
                (ds.field("MODIFIED_SEQUENCE") == sequence) &
                (ds.field("PRECURSOR_CHARGE") == charge)
            )
        ).to_table().to_pandas()

        # Create an ANNOTATION column, is the annotation for transitions and the native ID for precursors
        mask = ~df['PRODUCT_CHARGE'].isnull()
        df.loc[mask, 'ANNOTATION'] = (df.loc[mask, 'TRANSITION_TYPE'] +
                                       df.loc[mask, 'TRANSITION_ORDINAL'].astype(int).astype(str) + 
                                       '^' + 
                                       df.loc[mask, 'PRODUCT_CHARGE'].astype(int).astype(str))
        df.loc[~mask, 'ANNOTATION'] = df.loc[~mask, 'NATIVE_ID']

        chroms = []
        for _, row in df.iterrows():
            rt_data = OpenSwathXICParquetAccess._decodeArray(row['RT_DATA'], row['RT_COMPRESSION'])
            intensity_data = OpenSwathXICParquetAccess._decodeArray(row['INTENSITY_DATA'], row['INTENSITY_COMPRESSION'])
            chroms.append(Chromatogram(rt_data, intensity_data, row['ANNOTATION']))

        return chroms

    @staticmethod
    def _decodeArray(data, compr):
        numpress_config = po.NumpressConfig()
        result = []
        if compr == 0:
            return data
        if compr == 1:
            tmp = zlib.decompress(data)
            return struct.unpack("<%sd" % (len(tmp) // 8), tmp)
        elif compr == 5:
            tmp = bytearray(zlib.decompress(data))
            if len(tmp) > 0:
                numpress_config.setCompression('linear')
                po.MSNumpressCoder().decodeNP(base64.b64encode(tmp), result, False, numpress_config)
                return result
            else:
                return [0]
        elif compr == 6:
            tmp = bytearray( zlib.decompress(data) )
            if len(tmp) > 0:
                numpress_config.setCompression('slof')
                po.MSNumpressCoder().decodeNP(base64.b64encode(tmp), result, False, numpress_config)
                return result
            else:
                return [0]
        else:
            raise Exception(f"Compression type {compr} not supported")

    def getChromatogramDfFromSequenceAndCharge(self, sequence: str, charge: int) -> pd.DataFrame:
        '''
        Get chromatogram data as a dataframe
        '''
        chroms = self.getChromatogramsFromSequenceAndCharge(sequence, charge)
        chroms_df = []
        for c in chroms:
            chroms_df.append(c.toPandasDf())

        if len(chroms_df) == 0:
            return pd.DataFrame(columns=['rt', 'intensity', 'annotation'])
        else:
            return pd.concat(chroms_df)

    def __str__(self):
        return f"<OpenSwathXICParquetAccess(filename={self.filename})>"

    def __repr__(self):
        return f"OpenSwathXICParquetAccess(filename={self.filename})"
