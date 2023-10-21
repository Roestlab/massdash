#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
=========================================================================
            MassSeer 
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
from __future__ import print_function
import pandas as pd

class SqMassDataAccess(object):

    def __init__(self, filename):
        import sqlite3
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def getPrecursorChromIDs(self, precursor_id):
        """
        Get the chromatogram IDs for a given precursor ID
        """
        data = [row for row in self.c.execute(f"""SELECT ID, NATIVE_ID FROM CHROMATOGRAM WHERE NATIVE_ID LIKE '{precursor_id}_Precursor%'""")]
        return {"chrom_ids":[d[0] for d in data], "native_ids":[d[1] for d in data]}

    def getDataForChromatograms(self, ids):
        """
        Get data from multiple chromatograms chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        if len(ids) == 0:
            return [ [ [0], [0] ] ]

        stmt ="SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID IN ("
        for myid in ids:
            stmt += str(myid) + ","
        stmt = stmt[:-1]
        stmt += ")"

        data = [row for row in self.c.execute(stmt)]
        tmpres = self._returnDataForChromatogram(data)

        res = []
        for myid in ids:
            res.append( tmpres[myid] )
        return res

    def getDataForChromatogram(self, myid):
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID = %s" % myid )]
        return list(self._returnDataForChromatogram(data).values())[0]

    def getDataForChromatogramFromNativeId(self, native_id):
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA INNER JOIN CHROMATOGRAM ON CHROMATOGRAM.ID = CHROMATOGRAM_ID WHERE NATIVE_ID = %s" % native_id )]
        return list(self._returnDataForChromatogram(data).values())[0]

    def getDataForChromatogramsFromNativeIds(self, native_ids):
        """
        Get data from multiple chromatograms chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        if len(native_ids) == 0:
            return [ [ [0], [0] ] ]

        stmt ="SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA INNER JOIN CHROMATOGRAM ON CHROMATOGRAM.ID = CHROMATOGRAM_ID WHERE NATIVE_ID IN ("
        for myid in native_ids:
            stmt += str(myid) + ","
        stmt = stmt[:-1]
        stmt += ")"

        data = [row for row in self.c.execute(stmt)]
        tmpres = self._returnDataForChromatogram(data)

        chrom_ids = list(tmpres.keys())
        
        res = []
        for myid in chrom_ids:
            res.append( tmpres[myid] )
        return res

    def _returnDataForChromatogram(self, data):
        import PyMSNumpress
        import zlib

        # prepare result
        chr_ids = set([chr_id for chr_id, compr, data_type, d in data] )
        res = { chr_id : [None, None] for chr_id in chr_ids }

        rt_array = []
        intensity_array = []
        for chr_id, compr, data_type, d in data:
            result = []

            if compr == 5:
                # tmp = [ord(q) for q in zlib.decompress(d)]
                tmp = bytearray( zlib.decompress(d) )
                if len(tmp) > 0:
                    PyMSNumpress.decodeLinear(tmp, result)
                else:
                    result = [0]
            if compr == 6:
                # tmp = [ord(q) for q in zlib.decompress(d)]
                tmp = bytearray( zlib.decompress(d) )
                if len(tmp) > 0:
                    PyMSNumpress.decodeSlof(tmp, result)
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

import sqlite3
import pandas as pd

class OSWDataAccess(object):
    """
    A class for accessing data from an OpenSWATH SQLite database.

    Attributes:
        conn (sqlite3.Connection): A connection to the SQLite database.
        c (sqlite3.Cursor): A cursor for executing SQL statements on the database.
    """

    def __init__(self, filename):
        """
        Initializes a new instance of the OSWDataAccess class.

        Args:
            filename (str): The path to the SQLite database file.
        """
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def getProteinTable(self, include_decoys=False):
        """
        Retrieves the protein table from the database.

        Args:
            include_decoys (bool): Whether to include decoy proteins in the table.

        Returns:
            pandas.DataFrame: The protein table.
        """
        if include_decoys:
            stmt = "SELECT PROTEIN_ID, PEPTIDE_ID, PROTEIN_ACCESSION, PROTEIN.DECOY FROM PROTEIN INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = PROTEIN.ID INNER JOIN PEPTIDE ON PEPTIDE.ID = PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID"
        else:
            stmt = "SELECT PROTEIN_ID, PEPTIDE_ID, PROTEIN_ACCESSION, PROTEIN.DECOY FROM PROTEIN INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = PROTEIN.ID INNER JOIN PEPTIDE ON PEPTIDE.ID = PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID WHERE PROTEIN.DECOY = 0"

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPeptideTable(self, remove_ipf_peptides=True):
        """
        Retrieves the peptide table from the database.

        Args:
            remove_ipf_peptides (bool): Whether to remove IPF peptides from the table.

        Returns:
            pandas.DataFrame: The peptide table.
        """
        if remove_ipf_peptides:
            stmt = """SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID"""
        else:   
            stmt ="SELECT * FROM PEPTIDE"

        data = pd.read_sql(stmt, self.conn)

        return data

    # Method to get peptide table from protein_id
    def getPeptideTableFromProteinID(self, protein_id, remove_ipf_peptide=True):
        """
        Retrieves the peptide table from the database for a given protein ID.

        Args:
            protein_id (int): The protein ID.
            remove_ipf_peptides (bool): Whether to remove IPF peptides from the table.

        Returns:
            pandas.DataFrame: The peptide table.
        """
        if remove_ipf_peptide:
            stmt = f"""SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        WHERE PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = {protein_id}"""
        else:
            stmt = f"""SELECT PEPTIDE.*
                        FROM PEPTIDE
                        INNER JOIN PEPTIDE_PROTEIN_MAPPING ON PEPTIDE_PROTEIN_MAPPING.PEPTIDE_ID = PEPTIDE.ID
                        WHERE PEPTIDE_PROTEIN_MAPPING.PROTEIN_ID = {protein_id}"""

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPrecursorCharges(self, fullpeptidename):
        """
        Retrieves the precursor charges for a given peptide.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.

        Returns:
            pandas.DataFrame: The precursor charges.
        """
        stmt = f"SELECT CHARGE FROM PRECURSOR INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID INNER JOIN (SELECT * FROM PEPTIDE WHERE PEPTIDE.MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID"

        data = pd.read_sql(stmt, self.conn)

        return data

    def getPeptideTransitionInfo(self, fullpeptidename, charge):
        """
        Retrieves transition information for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The transition information.
        """
        stmt = f"""SELECT 
               PEPTIDE.ID AS PEPTIDE_ID,
               PRECURSOR.ID AS PRECURSOR_ID,
               TRANSITION.ID AS TRANSITION_ID,
               PEPTIDE.UNMODIFIED_SEQUENCE,
               PEPTIDE.MODIFIED_SEQUENCE,
               PRECURSOR.PRECURSOR_MZ,
               PRECURSOR.CHARGE AS PRECURSOR_CHARGE,
               PRECURSOR.LIBRARY_INTENSITY AS PRECURSOR_LIBRARY_INTENSITY,
               PRECURSOR.LIBRARY_RT AS PRECURSOR_LIBRARY_RT,
               PRECURSOR.LIBRARY_DRIFT_TIME AS PRECURSOR_LIBRARY_DRIFT_TIME,
               TRANSITION.PRODUCT_MZ,
               TRANSITION.CHARGE AS PRODUCT_CHARGE,
               TRANSITION.TYPE AS PRODUCT_TYPE,
               TRANSITION.ORDINAL AS PRODUCT_ORDINAL,
               TRANSITION.ANNOTATION AS PRODUCT_ANNOTATION,
               TRANSITION.LIBRARY_INTENSITY AS PRODUCT_LIBRARY_INTENSITY,
               TRANSITION.DETECTING AS PRODUCT_DETECTING,
               PEPTIDE.DECOY AS PEPTIDE_DECOY,
               PRECURSOR.DECOY AS PRECURSOR_DECOY,
               TRANSITION.DECOY AS TRANSITION_DECOY
               FROM (SELECT * FROM PRECURSOR WHERE PRECURSOR.CHARGE = {charge}) AS PRECURSOR
               INNER JOIN PRECURSOR_PEPTIDE_MAPPING ON PRECURSOR_PEPTIDE_MAPPING.PRECURSOR_ID = PRECURSOR.ID
               INNER JOIN (SELECT * FROM PEPTIDE WHERE PEPTIDE.MODIFIED_SEQUENCE = '{fullpeptidename}') AS PEPTIDE ON PEPTIDE.ID = PRECURSOR_PEPTIDE_MAPPING.PEPTIDE_ID
               INNER JOIN TRANSITION_PRECURSOR_MAPPING ON TRANSITION_PRECURSOR_MAPPING.PRECURSOR_ID = PRECURSOR.ID
               INNER JOIN TRANSITION ON TRANSITION.ID = TRANSITION_PRECURSOR_MAPPING.TRANSITION_ID"""

        data = pd.read_sql(stmt, self.conn)

        return data