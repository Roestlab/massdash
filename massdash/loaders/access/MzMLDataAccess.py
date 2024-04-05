"""
massdash/loaders/access/MzMLDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import click
from typing import List, Tuple, Literal
import itertools
from tqdm import tqdm
from joblib import Parallel, delayed
import traceback
import sys
import mmap
from pathlib import Path

# data modules
import pyopenms as po
import pandas as pd
import numpy as np

# Structs
from ...structs.TargetedDIAConfig import TargetedDIAConfig
from ...structs.FeatureMap import FeatureMap
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Internal
from ...util import LOGGER, method_timer, code_block_timer

class MzMLDataAccess():
    """
    Class for data loading and extracting operations of an .mzML file
    
    Attributes:
        filename (str): The mzML file to load.
        readOptions (str): The readOptions to use, either 'ondisk' or 'cached'.
        exp (OnDiscMSExperiment): The on disk experiment.
        meta_data (MSExperiment): The meta data.
        has_im (bool): Whether the data has ion mobility.
        
    Methods:
        load_data: Loads data from an mzML file as an on disc experiment for memory efficiency and meta data access without loading full data.
        get_target_ms_level_indices: Extract spectrum indices for a specific mslevel(s).
        get_spectra_rt_list: Get a list of RT for all the spectra using meta_exp.
    """

    def __init__(self, filename: str, readOptions="ondisk", verbose=False):
        """
        Initialise mzMLLoader object

        Args:
          mzml_file: (str) mzML file to load
          readOptions: (str) readOptions to use, either 'ondisk' or 'cached'
          verbose (bool): Enables verbose mode.
        """
        
        self.filename = filename
        self.runName = str(Path(filename).stem)
        self.readOptions = readOptions
        self.exp = po.OnDiscMSExperiment()
        self.meta_data = po.MSExperiment()
        self.has_im = self.check_ion_mobility()
        
        LOGGER.name = self.__class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

        
        self.load_data()

    def __str__(self):
        return f"MzMLDataAccess(filename={self.filename}, has_im={self.has_im})"
 
    def __repr__(self):
        return f"MzMLDataAccess(filename={self.filename}, has_im={self.has_im})"
    
    def check_ion_mobility(self, num_lines_to_check=10_000_000):
        """
        Check if the mzML file contains ion mobility data

        Args:
        mzml_file: (str) mzML file to load
        num_lines_to_check: (int) Number of lines to check for "Ion Mobility"

        Returns:
        Return a boolean indicating if the mzML file contains ion mobility data
        """
        has_ion_mobility = False
        mzml_file = self.filename
        with open(mzml_file, 'rb', 0) as file:
            s = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) 
            for line in iter(s.readline, b""):
                if b'Ion Mobility' in line:
                    has_ion_mobility = True
                    break 
                if s.tell() > num_lines_to_check:
                    break
        return has_ion_mobility

    @method_timer
    def load_data(self):
        """
        Method to load data from an mzML file as an on disc experiment for memory efficiency and meta data access without loading full data
        """

        if self.readOptions=="ondisk":
            with code_block_timer('Creating OnDiscExperiment...', LOGGER.debug):
                exp = po.OnDiscMSExperiment()

            with code_block_timer(f'Opening {self.filename} file...', LOGGER.info):
                exp.openFile(self.filename)

            with code_block_timer('Extracting meta data...', LOGGER.debug):
                meta_data = exp.getMetaData()

            LOGGER.info(
                f"There are {meta_data.getNrSpectra()} spectra and {exp.getNrChromatograms()} chromatograms.")
            LOGGER.info(
                f"There are {sum([spec.getMSLevel()==1  for spec in meta_data.getSpectra()])} MS1 spectra and {sum([spec.getMSLevel()==2  for spec in meta_data.getSpectra()])} MS2 spectra.")
        elif self.readOptions=="cached":
            # Because data is cached, we need to make an assumption about whether the file is MS1 or MS2
            with code_block_timer(f'Loading Cached Data from {self.filename} file...', LOGGER.info):
                exp = po.SpectrumAccessOpenMSCached(self.filename)
            ## Still need access to the meta data, so we need to create an on-disk experiment
            with code_block_timer('Creating OnDiscExperiment...', LOGGER.debug):
                od_exp = po.OnDiscMSExperiment()
            with code_block_timer(f'Opening {self.filename} file to extract meta-data...', LOGGER.info):
                od_exp.openFile(self.filename)
            with code_block_timer(f'Extracting meta data...', LOGGER.debug):
                meta_data = od_exp.getMetaData()
            # Delete OnDiskExperiment since we don't need it anymore, we only need the meta data
            del od_exp
    
            LOGGER.info(
                f"There are {exp.getNrSpectra()} spectra and {exp.getNrChromatograms()} chromatograms.")
            LOGGER.info(
                f"There are {sum([spec.getMSLevel()==1  for spec in meta_data.getSpectra()])} MS1 spectra and {sum([spec.getMSLevel()==2  for spec in meta_data.getSpectra()])} MS2 spectra.")
        else:
            click.ClickException(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")

        self.exp = exp
        self.meta_data = meta_data
            
    def get_target_ms_level_indices(self, mslevel=[1,2]) -> np.array:
        """
        Extract spectrum indices for a specific mslevel(s).

        Args:
          self: (object) self object containing meta_data
          mslevel: (list) list of mslevel(s) to extract indices for

        Return:
          Return mslevel_indices a list of indices with request mslevel(s) to self
        """
        if self.readOptions=="ondisk":
            spectra = self.meta_data.getSpectra()
            return np.array([indice for indice, spec in enumerate(
                spectra) if spec.getMSLevel() in mslevel])
        elif self.readOptions=="cached":
            return np.array(range(0,self.exp.getNrSpectra()))
        else:
            click.ClickException(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")

    def get_spectra_rt_list(self) -> np.array:
        """
        Get a list of RT for all the spectra using meta_exp

        Args:
          self: (object) self object containing meta_data

        Return:
          Return a list of RT values for spectra
        """
        if self.readOptions=="ondisk":
            meta_rt_list = np.array([meta_spec.getRT() for meta_spec in self.meta_data.getSpectra()])
        else: # self.readOptions=="cached"
            meta_rt_list = np.array([meta_spec.getRT()for meta_spec in self.meta_data.getSpectra()])
        return meta_rt_list
    
    def load_spectrum(self, spec_indice: int) -> Tuple[np.array, np.array, np.array]:
        """
        Load a single spectrum for a given spectrum indice.

        Args:
          spec_indice: (int) an interger of the spectrum indice to extra a spectrum for

        Return:
          mz_array: mz array
          int_array: intensity array
          im_array: ion mobility array 
        """
        # Get data arrays
        if (self.readOptions=="ondisk"):
            with code_block_timer(f'Extracting mz, int, im data arrays...', LOGGER.debug):
                spec = self.exp.getSpectrum(spec_indice)
                mz_array = spec.get_peaks()[0]
                int_array = spec.get_peaks()[1]
                if self.has_im:
                    im_array = spec.getFloatDataArrays()
                else:
                    im_array = []
        elif (self.readOptions=="cached"):
            spec = self.meta_data.getSpectrum(spec_indice)
            with code_block_timer(f'Extracting mz, int, im data arrays...', LOGGER.debug):
                das = self.exp.getSpectrumById(spec_indice).getDataArrays()
                mz_array = das[0].getData()
                int_array = das[1].getData()
                if self.has_im:
                    im_array = das[2].getData()
                else:
                    im_array = []
        else:
            LOGGER.error(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")
        
        return (mz_array, int_array, im_array)
 

    def filter_single_spectrum(self, 
                               spec_indice: int, 
                               feature: TransitionGroupFeature,
                               config: TargetedDIAConfig) -> po.MSSpectrum:
        """
        Filter a single spectrum for a given spectrum indice.

        Args:
          spec_indice: (int) an interger of the spectrum indice to extra a spectrum for
          feature: (TransitionGroupFeature) metadata on feature
          config: (TargetedDIAConfig object) an object of TargetedDIAConfig that contains configuration parameters of how wide filtering windows should be

        Return:
          po.MSSpectrum() a MSSpectrum object 
        """
        # create extraction parameters 
        if self.has_im:
            if feature.consensusApexIM is not None:
                im_start, im_end = config.get_im_upper_lower(feature.consensusApexIM)
            else:
                LOGGER.critical(f"ion mobility information not found in feature {feature.sequence} but present in mzML file")
        # Get tolerance bounds on coordinates
        target_precursor_mz_lower, target_precursor_mz_upper = config.get_upper_lower_tol(feature.precursor_mz)
        target_product_upper_lower_list = [config.get_upper_lower_tol(mz) for mz in feature.product_mz]

        spec_meta = self.meta_data.getSpectrum(spec_indice)


        writeSpectrum = False # boolean flag of whether to write out filtered spectrum

        if spec_meta.getMSLevel() == 1 and 1 in config.mslevel:
            mz_array, int_array, im_array = self.load_spectrum(spec_indice)
            # first filter IM
            if self.has_im:
                if (self.readOptions=="ondisk"): 
                    im_match_bool = (im_array[0].get_data() > im_start) & (
                        im_array[0].get_data() < im_end)
                elif (self.readOptions=="cached"):
                    im_match_bool = (im_array > im_start) & (
                        im_array < im_end)
            else:
                im_match_bool = np.ones(mz_array.shape)

            mz_match_bool = (mz_array > target_precursor_mz_lower) & (
                mz_array < target_precursor_mz_upper)

            writeSpectrum = any(mz_match_bool*im_match_bool)
            if writeSpectrum:
                LOGGER.debug(
                    f"Adding MS1 spectrum {spec_meta.getNativeID()} with spectrum indice {spec_indice} filtered for {sum(mz_match_bool*im_match_bool)} spectra between {target_precursor_mz_lower} m/z and {target_precursor_mz_upper} m/z") # and IM between {im_start} and {im_end}")


        elif spec_meta.getMSLevel() == 2 and 2 in config.mslevel:
            # Get SWATH windows upper and lower
            current_prec = spec_meta.getPrecursors()[0]

            swath_mz_win_lower = current_prec.getMZ() - current_prec.getIsolationWindowLowerOffset()
            swath_mz_win_upper = current_prec.getMZ() + current_prec.getIsolationWindowUpperOffset()

            # Only load and extract product spectra if current spectrums isolation window contains precursor mz
            if feature.precursor_mz > swath_mz_win_lower and feature.precursor_mz < swath_mz_win_upper:
                mz_array, int_array, im_array = self.load_spectrum(spec_indice)
                if self.has_im:
                    if (self.readOptions=="ondisk"): 
                        im_match_bool = (im_array[0].get_data() > im_start) & (
                            im_array[0].get_data() < im_end)
                    elif (self.readOptions=="cached"):
                        im_match_bool = (im_array > im_start) & (
                            im_array < im_end)
                else:
                    im_match_bool = np.ones(mz_array.shape)

                mz_match_bool = np.array(list(map(config.is_mz_in_product_mz_tol_window, mz_array, itertools.repeat(
                    target_product_upper_lower_list, len(mz_array)))))
                writeSpectrum = any(mz_match_bool*im_match_bool)
                if writeSpectrum:
                    LOGGER.debug(
                        f"Feature {feature.sequence}{feature.precursor_charge} - Adding MS2 spectrum {spec_meta.getNativeID()} with spectrum indice {spec_indice} filtered for {sum(mz_match_bool*im_match_bool)} spectra between {target_product_upper_lower_list} m/z") #and IM between {im_start} and {im_end}")
            else:
                LOGGER.debug(f"Feature {feature.sequence}{feature.precursor_charge} Skipping MS2 spectrum {spec_meta.getNativeID()} with spectrum indice {spec_indice} because current swath isolation window ({swath_mz_win_lower} m/z - {swath_mz_win_upper} m/z) does not contain target precursor m/z ({feature.consensusApex})")

        # Only write out filtered spectra if there is any fitlered spectra to write out
        spec_out = po.MSSpectrum()
        if writeSpectrum:
            with code_block_timer(f'Getting filtered spectrum...', LOGGER.debug):
                extract_target_indices = np.where(mz_match_bool * im_match_bool)
                filtered_mz = mz_array[extract_target_indices]
                filtered_int = int_array[extract_target_indices]
                if self.has_im:
                    if (self.readOptions=="ondisk"):
                        filtered_im = im_array[0].get_data()[extract_target_indices]
                    elif (self.readOptions=="cached"):
                        filtered_im = im_array[extract_target_indices]
                else:
                    filtered_im = []
                LOGGER.debug(f"INFO: Adding filtered mz data of length {len(filtered_mz)} | int of length {len(filtered_int)} | im of length {len(filtered_im)}")
                # replace peak data with filtered peak data
                spec_out.set_peaks((filtered_mz, filtered_int))
                
                if self.has_im:
                    # repalce float data arrays with filtered ion mobility data
                    fda = po.FloatDataArray()
                    filtered_im_np = np.array(filtered_im).astype(np.float32)
                    fda.set_data(filtered_im_np)
                    fda.setName("Ion Mobility")
                    spec_out.setFloatDataArrays([fda])
            
            spec_out.setMSLevel(spec_meta.getMSLevel())
            spec_out.setRT(spec_meta.getRT())
            # If you have a lot of filtered spectra to return, it becomes memory heavy.
            return spec_out

    @method_timer
    def reduce_spectra(self, feature: TransitionGroupFeature , config: TargetedDIAConfig) -> FeatureMap:
        """
        Main method for filtering raw mzML DIA/diaPASEF data given specific set of coordinates to filter for.

        Args:
            feature: (TransitionGroupFeature) a TransitionGroupFeature object that contains coordinates to filter for
            config: (TargetedDIAConfig object) an object of TargetedDIAConfig that contains configuration parameters of how wide filtering windows should be

        Return:
          FeatureMap: a FeatureMap object that contains filtered spectra
        """

        # Get indices for requested ms level spectra
        LOGGER.debug(f"Extracting indices for MS Levels: {config.mslevel}")

        # Initialize empty MSExperiment container to store filtered data
        filtered = po.MSExperiment()

       
        rt_start, rt_end = config.get_rt_upper_lower(feature.consensusApex)
         
        LOGGER.debug(
            f"Extracting spectra for {feature.sequence}{feature.precursor_charge} | RT: {feature.consensusApex} sec ({rt_start} - {rt_end})")

        # Restrict spectra list further for RT window, to reduce the number of spectra we need to check to perform filtering on
        use_rt_spec_indices = np.where(np.array(
            [spec_rt >= rt_start and spec_rt <= rt_end for spec_rt in self.get_spectra_rt_list()]))
        target_spectra_indices = np.intersect1d(
            self.get_target_ms_level_indices(config.mslevel), use_rt_spec_indices)
        
        with code_block_timer(f"Filtering {target_spectra_indices.shape[0]} Spectra for {feature.sequence}{feature.precursor_charge}...", LOGGER.debug):
            try:
                filt_spec_list = Parallel(n_jobs=1)(delayed(self.filter_single_spectrum)(spectrum_indice, feature, config) for spectrum_indice in target_spectra_indices.tolist())
            except:
                traceback.print_exc(file=sys.stdout)

        # Add filtered spectra to MSExperiment container
        filt_spec_list = list(
            filter(lambda spectra: spectra is not None, filt_spec_list))
        # Add filtered spectrum to filtered MSExperiment container
        _ = [filtered.addSpectrum(spec) for spec in filt_spec_list]

        #return filtered
        return self.msExperimentToFeatureMap(filtered, feature, config)

    # @method_timer
    def msExperimentToFeatureMap(self, msExperiment: po.MSExperiment, feature: TransitionGroupFeature, config: TargetedDIAConfig ) -> FeatureMap:
        """
        Convert filtered spectra to Pandas DataFrame

        Args:
            msExperiment: (MSExperiment) MSExperiment object that contains filtered data
            feature: (TransitionGroupFeature) metadata on feature
            config: (TargetedDIAConfig object) an object of TargetedDIAConfig that contains configuration parameters of how wide filtering windows should be
          
        Return:
            FeatureMap: a FeatureMap object that contains filtered spectra
        """
        results_df = pd.DataFrame()
        for k in range(msExperiment.getNrSpectra()):
            spec = msExperiment.getSpectrum(k)
            mz, intensity = spec.get_peaks()
            if (len(mz) == 0 and len(intensity) == 0):
                LOGGER.warning(
                    f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no m/z or intensity array, skipping this spectrum")
                continue
            rt = np.full([mz.shape[0]], spec.getRT(), float)
            
            if not self.has_im:
                if config.im_window is not None:
                    LOGGER.warning(
                        f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no ion mobility array")
                im = np.full([mz.shape[0]], np.nan, float)
            else:
                im_tmp = spec.getFloatDataArrays()[0]
                im = im_tmp.get_data()
                
            LOGGER.debug(
                f"Adding MS{spec.getMSLevel()} spectrum for peptide: {feature.sequence}{feature.precursor_charge} with native id: {spec.getNativeID()}")
            add_df = pd.DataFrame({'native_id': spec.getNativeID(), 'ms_level': spec.getMSLevel(), 'precursor_mz': feature.precursor_mz,
                                   'mz': mz, 'rt': rt, 'im': im, 'int': intensity})
            results_df = pd.concat([results_df, add_df])

        if not results_df.empty:
            ## Add annotation and column
            results_df['Annotation'] = results_df.apply(self._apply_mz_mapping, args=(feature.product_mz, feature.product_annotations) , axis=1)
            
            ## Add product/precursor mz column
            annotation_mz_mapping = pd.DataFrame({'Annotation': feature.product_annotations, 'product_mz': feature.product_mz})
            annotation_mz_mapping = pd.concat([annotation_mz_mapping, pd.DataFrame({'Annotation': ['prec'], 'product_mz': [feature.precursor_mz]})])
            results_df = results_df.merge(annotation_mz_mapping, on='Annotation', how='left')
        else:
            LOGGER.warning(f"No spectra found for peptide: {feature.sequence}{feature.precursor_charge}. Try adjusting the extraction parameters")
            results_df = pd.DataFrame(columns=['rt', 'int', 'Annotation'])

        return FeatureMap(results_df, feature.sequence, feature.precursor_charge, config)
    
    @staticmethod
    def _find_closest_reference_mz(given_mz: np.array, reference_mz_values: np.array, peptide_product_annotation_list: np.array) -> np.array:
        """
        Find the closest reference m/z value in the given list to provided m/z values.
        Args:
            given_mz (np.array): An array of m/z values for which to find the closest reference m/z values.
            reference_mz_values (np.array): An array of reference m/z values to compare against.
            peptide_product_annotation_list (np.array): An array of reference m/z value annotations.
        Returns:
            np.array: An array of the closest reference m/z values annotations from the provided list.
        """
        return peptide_product_annotation_list[np.argmin(np.abs(reference_mz_values - given_mz))]

    @staticmethod
    def _apply_mz_mapping(row: pd.Series, peptide_product_mz_list: List[float], peptide_product_annotation_list: List[str]) -> Literal["float", "np.nan"]:
        """
        Apply mz mapping to the given row based on the ms_level.
        Args:
            row (pd.Series): The row containing the data.
            peptide_product_mz_list (List): The list of peptide product m/z values.
            peptide_product_annotation_list (List): The list of peptide product annotations.
        Returns:
            Union[float, np.nan]: The mapped m/z value.
        """
        if row['ms_level'] == 2:
            return MzMLDataAccess._find_closest_reference_mz(row['mz'], np.array(peptide_product_mz_list), np.array(peptide_product_annotation_list))
        elif row['ms_level'] == 1:
            return 'prec'
        else:
            raise ValueError(f"Unknown ms_level {row['ms_level']} encountered.")

