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
        
        df = self.parquet.filter(
            pc.and_(
                pc.equal(pc.field("SEQUENCE"), sequence),
                pc.equal(pc.field("CHARGE"), charge)
            )
        ).select(['RT_DATA', 'INTENSITY_DATA', 'RT_COMPRESSION', 'INTENSITY_COMPRESSION']).to_table().to_pandas()

        chroms = []
        for row in df.iterrows():
            rt_data = self._decodeArray(row['RT_DATA'], row['RT_COMPRESSION'])
            intensity_data = self._decodeArray(row['INTENSITY_DATA'], row['INTENSITY_COMPRESSION'])
            chroms.append(Chromatogram(rt_data, intensity_data, sequence))

        return chroms
    
    def _decodeArray(self, data, compr):
        numpress_config = po.NumpressConfig()
        result = []
        if compr == 0:
            return data
        if compr == 1:
            tmp = zlib.decompress(data)
            return struct.unpack("<%sd" % (len(tmp) // 8), tmp)
        elif compr == 5:
            tmp = bytearray( zlib.decompress(data) )
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

    def getDataForChromatogramsDf(self, sequence: str, charge: int) -> pd.DataFrame:
        '''
        Get chromatogram data as a dataframe
        '''
        chroms = self.getChromatogramsFromSequenceAndCharge(sequence, charge)
        chroms_df = []
        for c in chroms:
            chroms_df.append(c.toPandasDf())

        if len(c) == 0:
            return pd.DataFrame(columns=['rt', 'intensity', 'annotation'])
        else:
            return pd.concat(c)

    def getDataForChromatograms(self, ids: List[str], labels: List[str]) -> List[Chromatogram]:
        """
        Get 
        Get data from multiple chromatograms chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        if len(ids) == 0:
            return [ [ [0], [0] ] ]

        res = self._getChromatogramsHelper(ids, labels)

        ### Convert to chromatograms
        ### match ids with labels
        c = []
        for l, val in zip(labels, res.values()):
            c.append(Chromatogram(val[0], val[1], l))

        return c

    def getDataForChromatogramsFromNativeIdsDf(self, native_ids: List[str], labels: List[str]) -> pd.DataFrame:
        '''
        Get chromatogram data as a dataframe
        '''
        if len(native_ids) == 0:
            return pd.DataFrame(columns=['rt', 'intensity', 'annotation'])

        res = self._getChromatogramsHelperFromNativeIds(native_ids)

        c = []
        for l, val in zip(labels, res.values()):
            c.append(Chromatogram(val[0], val[1], l).toPandasDf())

        if len(c) == 0:
            return pd.DataFrame(columns=['rt', 'intensity', 'annotation'])
        else:
            return pd.concat(c)

    def getDataForChromatogramsFromNativeIds(self, native_ids: List, labels: List[str]) -> List[Chromatogram]:
        """
        Get data from multiple chromatograms chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        if len(native_ids) == 0:
            return [ [ [0], [0] ] ]
        
        res = self._getChromatogramsHelperFromNativeIds(native_ids)

        ### Convert to chromatograms
        ### match ids with labels
        c = []
        for l, val in zip(labels, res.values()):
            c.append(Chromatogram(val[0], val[1], l))

        return c

    def _returnDataForChromatogram(self, data):
        # prepare result
        chr_ids = [chr_id for chr_id, compr, data_type, d in data]
        res = OrderedDict()
        numpress_config = po.NumpressConfig()
        for i in chr_ids:
            res[i] = [None, None]


        for chr_id, compr, data_type, d in data:
            result = []

            if compr == 1:
                tmp = zlib.decompress(d)
                result = struct.unpack("<%sd" % (len(tmp) // 8), tmp)

            if compr == 5:
                # tmp = [ord(q) for q in zlib.decompress(d)]
                tmp = bytearray( zlib.decompress(d) )
                if len(tmp) > 0:
                    numpress_config.setCompression('linear')
                    po.MSNumpressCoder().decodeNP(base64.b64encode(tmp), result, False, numpress_config)
                else:
                    result = [0]
            if compr == 6:
                # tmp = [ord(q) for q in zlib.decompress(d)]
                tmp = bytearray( zlib.decompress(d) )
                if len(tmp) > 0:
                    numpress_config.setCompression('slof')
                    po.MSNumpressCoder().decodeNP(base64.b64encode(tmp), result, False, numpress_config)
                else:
                    result = [0]

            if len(result) == 0:
                result = [ 0 ]
            if data_type == 1:
                res[chr_id][1] = result
            elif data_type == 2:
                res[chr_id][0] = result
            else:
                raise Exception("Only expected RT or Intensity data for chromatogram")

        return res
    
    def __str__(self):
        return f"SqMassDataAccess(filename={self.filename})"
 
    def __repr__(self):
        return f"SqMassDataAccess(filename={self.filename})"
