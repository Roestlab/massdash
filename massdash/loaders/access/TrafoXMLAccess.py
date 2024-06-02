"""
massdash/loaders/access/TrafoXMLAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Dict, Tuple
from os.path import basename
import xml.etree.ElementTree as ET
import pandas as pd


# Library Access
from ..SpectralLibraryLoader import SpectralLibraryLoader

class TrafoXMLAccess:
    """
    A class for accessing and loading data from a TrafoXML file.

    Args:
        input_file (str): The path to the TrafoXML file.
        irt_library (str, optional): The path to the IRT library file. Defaults to None.

    Attributes:
        input_file_str (str): The path to the TrafoXML file.
        tree (ElementTree): The parsed XML tree from the TrafoXML file.
        root (Element): The root element of the XML tree.
        irt_library_str (str): The path to the IRT library file.
        irt_library (SpectralLibraryLoader): The loaded IRT library.

    Methods:
        load_transformation_params: Loads the transformation parameters from the TrafoXML file.
        load_pairs: Loads the transformation pairs from the TrafoXML file.
        load_pairs_df: Loads the transformation pairs as a pandas DataFrame.
    """

    def __init__(self, 
                 input_file: str, 
                 irt_library: str = None, 
                 mzDebugFile: str = None, 
                 imDebugFile: str = None) -> None:
        self.input_file_str = input_file
        self.tree = ET.parse(self.input_file_str)
        self.root = self.tree.getroot()
        self.irt_library_str = irt_library
        self.mzDebugFile_str = mzDebugFile
        self.imDebugFile_str = imDebugFile
        
        if self.irt_library_str is not None:
            self.irt_library = SpectralLibraryLoader(self.irt_library_str)
            self.irt_library.load()
        
        if self.mzDebugFile_str is not None:
            self.mzDebugFile = pd.read_csv(self.mzDebugFile_str, sep='\t')
            
        if self.imDebugFile_str is not None:
            self.imDebugFile = pd.read_csv(self.imDebugFile_str, sep='\t')

    def load_transformation_params(self) -> Dict:
        """
        Loads the transformation parameters from the TrafoXML file.

        Returns:
            dict: A dictionary containing the transformation parameters.

        """
        transformation = self.root.find('Transformation')
        params = {param.attrib['name']: param.attrib['value'] for param in transformation.findall('Param')}
        return params

    def load_pairs(self) -> List[Tuple[float, float]]:
        """
        Loads the transformation pairs from the TrafoXML file.

        Returns:
            List[Tuple[float, float]]: A list of tuples representing the transformation pairs.

        """
        transformation = self.root.find('Transformation')
        pairs = [(float(pair.attrib['from']), float(pair.attrib['to'])) for pair in transformation.find('Pairs')]
        return pairs
    
    def load_pairs_df(self) -> pd.DataFrame:
        """
        Loads the transformation pairs as a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the transformation pairs.

        """
        pairs = self.load_pairs()
        df = pd.DataFrame(pairs, columns=['experiment_rt', 'library_rt'])
        
        # Add irt precursor information to table if irt_library is available
        if self.irt_library_str is not None:
            irt_prec_meta = self.irt_library.data[['GeneName', 'ProteinId', 'ModifiedPeptideSequence',
       'PrecursorMz', 'PrecursorCharge', 'ProductMz', 'ProductCharge', 'Annotation', 'NormalizedRetentionTime',
       'PrecursorIonMobility']].drop_duplicates()
            df = pd.merge(df, irt_prec_meta, left_on='library_rt', right_on='NormalizedRetentionTime', how='inner')
            
        if self.mzDebugFile_str is not None:
            df = pd.merge(df, self.mzDebugFile, left_on='experiment_rt', right_on='RT', how='inner')
            # Drop RT column, since it's the same as experiment_rt
            df = df.drop(columns=['RT'])
            
        if self.imDebugFile_str is not None:
            df = pd.merge(df, self.imDebugFile[['RT', 'im', 'theo_im', 'intensity']], left_on='experiment_rt', right_on='RT', how='inner')
            # Drop RT column, since it's the same as experiment_rt
            df = df.drop(columns=['RT'])
            
        df['filename'] = basename(self.input_file_str).split('.')[0]

        return df
