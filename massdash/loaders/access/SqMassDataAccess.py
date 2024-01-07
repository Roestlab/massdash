"""
massdash/loaders/access/SqMassDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
=========================================================================
            MassDash 
=========================================================================

Copyright (c) 2013, ETH Zurich
For a full list of authors, refer to the file AUTHORS.

This software is released under a three-clause BSD license:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of any author or any participating institution
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
--------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
$Maintainer: Justin Sing$
$Authors: Hannes Roest, Justin Sing$
--------------------------------------------------------------------------
"""

from typing import List
from collections import OrderedDict
import pyopenms as po
import sqlite3
import pandas as pd
import base64
import struct
import zlib

# Structs
from ...structs.Chromatogram import Chromatogram
# Utils
from ...util import check_sqlite_column_in_table, check_sqlite_table

class SqMassDataAccess:

    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        self.filename = filename

    def getPrecursorChromIDs(self, precursor_id):
        """
        Get the chromatogram IDs for a given precursor ID
        """
        data = [row for row in self.c.execute(f"""SELECT ID, NATIVE_ID FROM CHROMATOGRAM WHERE NATIVE_ID LIKE '{precursor_id}_Precursor%'""")]
        return {"chrom_ids":[d[0] for d in data], "native_ids":[d[1] for d in data]}


    def _getChromatogramsHelper(self, ids: List[str], labels: List[str]):
        """
        Helper function to get chromatogram data, assumes that ids are not empty
        """
        stmt ="SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID IN ("
        for myid in ids:
            stmt += str(myid) + ","
        stmt = stmt[:-1]
        stmt += ")"

        data = [row for row in self.c.execute(stmt)]
        return self._returnDataForChromatogram(data)
    
    def _getChromatogramsHelperFromNativeIds(self, native_ids: List[str]):
        stmt ="SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA INNER JOIN CHROMATOGRAM ON CHROMATOGRAM.ID = CHROMATOGRAM_ID WHERE NATIVE_ID IN ("
        for myid in native_ids:
            stmt += str(myid) + ","
        stmt = stmt[:-1]
        stmt += ")"

        data = [row for row in self.c.execute(stmt)]
        return self._returnDataForChromatogram(data)

    def getDataForChromatogramsDf(self, ids: List[str], labels: List[str]) -> pd.DataFrame:
        '''
        Get chromatogram data as a dataframe
        '''
        if len(ids) == 0:
            return pd.DataFrame(columns=['rt', 'intensity', 'annotation'])

        res = self._getChromatogramsHelper(ids, labels)

        c = []
        for l, val in zip(labels, res.values()):
            c.append(Chromatogram(val[0], val[1], l).toPandasDf())

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

    def getDataForChromatogram(self, myid: str, label: str) -> Chromatogram:
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID = %s" % myid )]
        res = list(self._returnDataForChromatogram(data).values())[0]
        return Chromatogram(res[0], res[1], label)

    def getDataForChromatogramFromNativeId(self, native_id):
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA INNER JOIN CHROMATOGRAM ON CHROMATOGRAM.ID = CHROMATOGRAM_ID WHERE NATIVE_ID = %s" % native_id )]
        return list(self._returnDataForChromatogram(data).values())[0]

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
        chr_ids = set([chr_id for chr_id, compr, data_type, d in data] )
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
