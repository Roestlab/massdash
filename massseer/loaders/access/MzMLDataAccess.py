import click
from typing import List, Tuple
import itertools
import tqdm
from joblib import Parallel, delayed
import traceback
import sys
import mmap

# data modules
import pyopenms as po
import pandas as pd
import numpy as np

# Structs
from massseer.structs.TargetedDIAConfig import TargetedDIAConfig
from massseer.structs.FeatureMap import FeatureMap
# Internal
from massseer.util import LOGGER, method_timer, code_block_timer

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
        self.readOptions = readOptions
        self.exp = po.OnDiscMSExperiment()
        self.meta_data = po.MSExperiment()
        self.has_im = self.check_ion_mobility()
        
        LOGGER.name = self.__class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def __str__(self):
        return f"mzMLLoader(filename={self.filename}, has_im={self.has_im})"
 
    def __repr__(self):
        return f"mzMLLoader(filename={self.filename}, has_im={self.has_im})"
    
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
        elif self.readOptions=="cached":
            meta_rt_list = np.array([meta_spec.getRT()for meta_spec in self.meta_data.getSpectra()])
        else:
            click.ClickException(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")
        self.meta_rt_list = meta_rt_list
    
    def filter_single_spectrum(self, 
                               spec_indice: int, 
                               mslevel: List[int], 
                               target_peptide_group: str,
                               im_start: float, 
                               im_end: float, 
                               target_precursor_mz: float, 
                               target_precursor_mz_lower: float, target_precursor_mz_upper: float, target_product_upper_lower_list: List[Tuple[float, float]]
                               ) -> po.MSSpectrum:
        """
        Filter a single spectrum for a given spectrum indice.

        Args:
          self: (TargetedDIADataAccess object) an object of self that contains an experiment of OnDiskMSExperiment
          spec_indice: (int) an interger of the spectrum indice to extra a spectrum for
          mslevel: (list) a list of intergers for ms levels to filter for
          target_peptide: (str) target peptide sequence string to set as meta data
          im_start: (float) start of ion mobility window to filter for 
          im_end: (float) end of ion mobility window to filter for 
          target_precursor_mz_lower: (float) the lower acceptable bound of the target precursor within m/z tolerance 
          target_precursor_mz_upper: (float) the upper acceptable bound of the target precursor within m/z tolerance 
          target_product_upper_lower_list: (list) a list of tuples containing lower and upper bound for target product m/z within m/z tolerance


        Return:
          If self contains a consumer, filtered spectrum is written to disk, otherwise the filtered spectrum MSSpectrum object is retuned
        """
        # Get data arrays
        if (self.readOptions=="ondisk"):
            with code_block_timer(f'Extracting mz, int, im data arrays...', LOGGER.debug):
                spec = self.mzmlData.exp.getSpectrum(spec_indice)
                mz_array = spec.get_peaks()[0]
                int_array = spec.get_peaks()[1]
                if self.mzmlData.has_im:
                    im_array = spec.getFloatDataArrays()
                else:
                    im_array = []
        elif (self.readOptions=="cached"):
            spec = self.mzmlData.meta_data.getSpectrum(spec_indice)
            with code_block_timer(f'Extracting mz, int, im data arrays...', LOGGER.debug):
                das = self.mzmlData.exp.getSpectrumById(spec_indice).getDataArrays()
                mz_array = das[0].getData()
                int_array = das[1].getData()
                if self.mzmlData.has_im:
                    im_array = das[2].getData()
                else:
                    im_array = []
        else:
            LOGGER.error(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")
        
        if len(spec.getPrecursors()) == 0:
            LOGGER.warn(
                f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no precursor, skipping this spectrum")
            return spec

        # Get SWATH windows upper and lower
        current_prec = spec.getPrecursors()[0]

        swath_mz_win_lower = current_prec.getMZ() - current_prec.getIsolationWindowLowerOffset()
        swath_mz_win_upper = current_prec.getMZ() + current_prec.getIsolationWindowUpperOffset()

        if self.mzmlData.has_im:
            if (self.readOptions=="ondisk"): 
                im_match_bool = (im_array[0].get_data() > im_start) & (
                    im_array[0].get_data() < im_end)
            elif (self.readOptions=="cached"):
                im_match_bool = (im_array > im_start) & (
                    im_array < im_end)
        else:
            im_match_bool = np.ones(mz_array.shape)
        
        if spec.getMSLevel() == 1 and 1 in mslevel:
            mz_match_bool = (mz_array > target_precursor_mz_lower) & (
                mz_array < target_precursor_mz_upper)
            if any(mz_match_bool*im_match_bool):
                LOGGER.debug(
                    f"Adding MS1 spectrum {spec.getNativeID()} with spectrum indice {spec_indice} filtered for {sum(mz_match_bool*im_match_bool)} spectra between {target_precursor_mz_lower} m/z and {target_precursor_mz_upper} m/z and IM between {im_start} and {im_end}")
        elif spec.getMSLevel() == 2 and 2 in mslevel:
            # Only extract product spectra if current spectrums isolation window contains precursor mz
            if target_precursor_mz > swath_mz_win_lower and target_precursor_mz < swath_mz_win_upper:
                mz_match_bool = np.array(list(map(self.is_mz_in_product_mz_tol_window, mz_array, itertools.repeat(
                    target_product_upper_lower_list, len(mz_array)))))
                if any(mz_match_bool*im_match_bool):
                    LOGGER.debug(
                        f"Adding MS2 spectrum {spec.getNativeID()} with spectrum indice {spec_indice} filtered for {sum(mz_match_bool*im_match_bool)} spectra between {target_product_upper_lower_list} m/z and IM between {im_start} and {im_end}")
            else:
                mz_match_bool = np.zeros(mz_array.shape).astype(bool)
                LOGGER.debug(f"Skipping MS2 spectrum {spec.getNativeID()} with spectrum indice {spec_indice} because current swath isolation window ({swath_mz_win_lower} m/z - {swath_mz_win_upper} m/z) does not contain target precursor m/z ({target_precursor_mz})")


        # Only write out filtered spectra if there is any fitlered spectra to write out
        if any(mz_match_bool*im_match_bool):
            with code_block_timer(f'Getting filtered spectrum...', LOGGER.debug):
                extract_target_indices = np.where(mz_match_bool * im_match_bool)
                filtered_mz = mz_array[extract_target_indices]
                filtered_int = int_array[extract_target_indices]
                if self.mzmlData.has_im:
                    if (self.readOptions=="ondisk"):
                        filtered_im = im_array[0].get_data()[extract_target_indices]
                    elif (self.readOptions=="cached"):
                        filtered_im = im_array[extract_target_indices]
                else:
                    filtered_im = []
                LOGGER.warn(f"INFO: Adding filtered mz data of length {len(filtered_mz)} | int of length {len(filtered_int)} | im of length {len(filtered_im)}")
                # replace peak data with filtered peak data
                spec.set_peaks((filtered_mz, filtered_int))
                
                if self.mzmlData.has_im:
                    # repalce float data arrays with filtered ion mobility data
                    fda = po.FloatDataArray()
                    filtered_im_np = np.array(filtered_im).astype(np.float32)
                    fda.set_data(filtered_im_np)
                    fda.setName("Ion Mobility")
                    spec.setFloatDataArrays([fda])
                    
                # Set peptide meta data
                spec.setMetaValue(
                    'peptide', self.peptides[target_peptide_group]['peptide'])
                spec.setMetaValue(
                    'precursor_mz', self.peptides[target_peptide_group]['precursor_mz'])    
                [spec.setMetaValue(f'product_mz_{i}', mz) for i, mz in zip(range(0, len(np.unique(self.peptides[target_peptide_group]['product_mz']))), np.unique(self.peptides[target_peptide_group]['product_mz']))]
                if 'rt_apex' in self.peptides[target_peptide_group].keys():
                    spec.setMetaValue(
                    'rt_apex', self.peptides[target_peptide_group]['rt_apex'])
                if 'im_apex' in self.peptides[target_peptide_group].keys():
                    spec.setMetaValue(
                    'im_apex', self.peptides[target_peptide_group]['im_apex'])
                if 'rt_boundaries' in self.peptides[target_peptide_group].keys():
                    spec.setMetaValue(
                    'rt_left_width', self.peptides[target_peptide_group]['rt_boundaries'][0])
                    spec.setMetaValue(
                    'rt_right_width', self.peptides[target_peptide_group]['rt_boundaries'][1])
                precursor = po.Precursor()
                precursor.setCharge(int(self.peptides[target_peptide_group]['charge']))
                precursor.setMZ(current_prec.getMZ())
                precursor.setIsolationWindowLowerOffset(current_prec.getIsolationWindowLowerOffset())
                precursor.setIsolationWindowUpperOffset(current_prec.getIsolationWindowUpperOffset())
                spec.setPrecursors([precursor])
                
            # If you have a lot of filtered spectra to return, it becomes memory heavy.
            return spec

    @method_timer
    def reduce_spectra(self, peptides: dict, config: TargetedDIAConfig) -> FeatureMap:
        """
        Main method for filtering raw mzML DIA/diaPASEF data given specific set of coordinates to filter for.

        Args:
            self: (TargetedDIADataAccess object) an object of self that contains an experiment of OnDiskMSExperiment
            peptide_transition_list: (dict) a dictionary of the transition m/z to extract and its annotation 
            precursor_mz: (float) the precursor m/z to extract
            rt: (float) the retention time to extract
            im: (float) the ion mobility to extract
            config: (TargetedDIAConfig object) an object of TargetedDIAConfig that contains configuration parameters

        Return:
          None
        """

        self.peptides = peptides

        # Get indices for requested ms level spectra
        LOGGER.debug(f"Extracting indices for MS Levels: {config.mslevel}")
        mslevel_indices = self.get_target_ms_level_indices(config.mslevel)

        # Get RT of spectra
        LOGGER.debug(f"Extracting RT values across spectra")
        rt_list = self.get_spectra_rt_list()
        LOGGER.debug(f"RT Range: {rt_list.min()} - {self.rt_list.max()}")

        # Initialize empty MSExperiment container to store filtered data
        filtered = po.MSExperiment()
        pbar = tqdm(self.peptides.keys())
        pbar_desc = "INFO: Processing"
        for target_peptide_group in pbar:
            # Update progess bar description
            pbar_desc = f"INFO: Processing..{target_peptide_group}"
            pbar.set_description(pbar_desc)

            # Get Coordinates for current peptide
            target_precursor_mz = self.peptides[target_peptide_group]['precursor_mz']
            target_product_mz = np.unique(self.peptides[target_peptide_group]['product_mz'])
            rt_apex = self.peptides[target_peptide_group]['rt_apex']
            im_apex = self.peptides[target_peptide_group]['im_apex']

            # Get tolerance bounds on coordinates
            target_precursor_mz_lower, target_precursor_mz_upper = config.get_upper_lower_tol(target_precursor_mz, config.ms1_mz_tol)
            target_product_upper_lower_list = [config.get_upper_lower_tol(mz, config.mz_tol) for mz in target_product_mz]

            rt_start, rt_end = config.get_rt_upper_lower(rt_apex)
            im_start, im_end = config.get_im_upper_lower(im_apex)

            LOGGER.debug(
                f"Extracting data for {target_peptide_group} | target precursor: {target_precursor_mz} m/z ({target_precursor_mz_lower} - {target_precursor_mz_upper}) | RT: {rt_apex} sec ({rt_start} - {rt_end}) | IM: {im_apex} 1/Ko ({im_start} - {im_end})")

            # Restrict spectra list further for RT window, to reduce the number of spectra we need to check to perform filtering on
            use_rt_spec_indices = np.where(np.array(
                [spec_rt >= rt_start and spec_rt <= rt_end for spec_rt in rt_list]))
            target_spectra_indices = np.intersect1d(
                mslevel_indices, use_rt_spec_indices)

            with code_block_timer(f"Filtering {target_spectra_indices.shape[0]} Spectra for {target_peptide_group}...", LOGGER.debug):
                try:
                    filt_spec_list = Parallel(n_jobs=1)(delayed(self.filter_single_spectrum)(spectrum_indice, config.mslevel, target_peptide_group, im_start, im_end, target_precursor_mz, target_precursor_mz_lower, target_precursor_mz_upper, target_product_upper_lower_list) for spectrum_indice in target_spectra_indices.tolist())
                except:
                    traceback.print_exc(file=sys.stdout)

            # Add filtered spectra to MSExperiment container
            filt_spec_list = list(
                filter(lambda spectra: spectra is not None, filt_spec_list))
            # Add filtered spectrum to filtered MSExperiment container
            _ = [filtered.addSpectrum(spec) for spec in filt_spec_list]

        return self.msExperimentToFeatureMap(filtered)

    @method_timer
    def msExperimentToFeatureMap(self, msExperiment: po.MSExperiment ) -> FeatureMap:
        """
        Convert filtered spectra to Pandas DataFrame

        Args:
            self: (object) self object that contains filtered data
            ms_level: (list) list of ms level data to filter for
          
        Return:
            Pandas DataFrame of the filtered spectra
        """
        results_df = pd.DataFrame()
        for k in tqdm(range(msExperiment.getNrSpectra())):
            spec = msExperiment.getSpectrum(k)
            mz, intensity = spec.get_peaks()
            if (len(mz) == 0 and len(intensity) == 0):
                LOGGER.warn(
                    f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no m/z or intensity array, skipping this spectrum")
                continue
            rt = np.full([mz.shape[0]], spec.getRT(), float)
            
            if not self.has_im:
                LOGGER.warn(
                    f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no ion mobility array")
                im = np.full([mz.shape[0]], np.nan, float)
            else:
                im_tmp = spec.getFloatDataArrays()[0]
                im = im_tmp.get_data()
                
            if len(spec.getPrecursors()) == 0:
                LOGGER.warn(
                    f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no precursor, skipping this spectrum")
                continue
                
            precursor = spec.getPrecursors()[0]
            LOGGER.debug(
                f"Adding MS{spec.getMSLevel()} spectrum for peptide: {spec.getMetaValue('peptide')} with native id: {spec.getNativeID()}")
            add_df = pd.DataFrame({'native_id': spec.getNativeID(), 'ms_level': spec.getMSLevel(), 'peptide': spec.getMetaValue(
                'peptide'), 'precursor_mz': spec.getMetaValue('precursor_mz'), 'charge': precursor.getCharge(), 'mz': mz, 'rt': rt, 'im': im, 'int': intensity})
            ## Add additional meta data
            meta_data = pd.DataFrame()
            if spec.getMetaValue('rt_apex') is not None:
                meta_data['rt_apex'] = pd.Series(spec.getMetaValue('rt_apex'))
            if spec.getMetaValue('im_apex') is not None:
                meta_data['im_apex'] = pd.Series(spec.getMetaValue('im_apex'))
            if spec.getMetaValue('rt_left_width') is not None:
                meta_data['rt_left_width'] = pd.Series(spec.getMetaValue('rt_left_width'))    
            if spec.getMetaValue('rt_right_width') is not None:
                meta_data['rt_right_width'] = pd.Series(spec.getMetaValue('rt_right_width'))
            if not meta_data.empty:
                add_df = add_df.join(meta_data, how='cross')
            results_df = pd.concat([results_df, add_df])
        return results_df
