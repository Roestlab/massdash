import sys
from typing import Union, List, Tuple
import traceback
from tqdm import tqdm

# data modules
import pyopenms as po
import numpy as np 
import pandas as pd
import itertools
from joblib import Parallel, delayed

# Internal
from massseer.loaders.access.MzMLDataAccess import MzMLDataAccess
from massseer.util import LOGGER, method_timer, code_block_timer
class TargetedDIADataAccess:
    """
    Class for a targeted DIA-PASEF data extraction
    
    Attributes:
        mzmlData (mzMLDataAccess): An mzMLDataAccess object containing the raw data.
        filename (str): The filename of the mzML file.
        readOptions (str): The read options for the mzML file.
        ms1_mz_tol (float): The m/z tolerance for MS1 spectra.
        mz_tol (float): The m/z tolerance for MS2 spectra.
        rt_window (float): The retention time window for spectra.
        im_window (float): The ion mobility window for spectra.
        mslevel (list): A list of MS levels to include.
        
    Methods:
        update: Update the configuration attributes using a dictionary.
        get_upper_lower_tol: Get the upper and lower bounds of a target m/z value given a tolerance.
        get_rt_upper_lower: Get the upper and lower bounds of a target retention time value given a window.
        get_im_upper_lower: Get the upper and lower bounds of a target ion mobility value given a window.
        is_mz_in_product_mz_tol_window: Check if a target m/z value is within a given tolerance window.
        filter_single_spectrum: Filter a single spectrum for a given spectrum index.
        reduce_spectra: Reduce the spectra for a given peptide.
        get_df: Convert filtered spectra to Pandas DataFrame.
    """
    def __init__(self, mzmlData: MzMLDataAccess, config: TargetedDIAConfig, readOptions: Union['ondisk', 'cached']='ondisk', verbose: bool=False):
        self.mzmlData = mzmlData
        self.filename = self.mzmlData.filename
        self.readOptions = readOptions
        # Configuration
        self.ms1_mz_tol = config.ms1_mz_tol
        self.mz_tol = config.mz_tol
        self.rt_window = config.rt_window
        self.im_window = config.im_window
        self.mslevel = config.mslevel
        
        LOGGER.name = "TargetedDIADataAccess"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
    
    def __str__(self):
        return f"TargetedDIADataAccess(filename={self.filename})"
 
    def __repr__(self):
        return f"TargetedDIADataAccess(filename={self.filename})"

    def update(self, config_dict: dict) -> None:
        """
        Update the configuration attributes using a dictionary.

        Args:
            config_dict (dict): A dictionary containing configuration values.
        """
        print("Info: Updating TargetedDIADataAccess config from dictionary")
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)



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
    def reduce_spectra(self, peptides: dict, config: TargetedDIAConfig) -> None:
        """
        Main method for filtering raw mzML DIA/diaPASEF data given specific set of coordinates to filter for.

        Args:
            self: (TargetedDIADataAccess object) an object of self that contains an experiment of OnDiskMSExperiment
            peptides: (dict) a dictionary of peptide sequences as keys and a dictionary of peptide meta data as values
            config: (TargetedDIAConfig object) an object of TargetedDIAConfig that contains configuration parameters

        Return:
          None
        """

        # Config for targeted extraction parameters
        self.update(config)

        self.peptides = peptides

        # Get indices for requested ms level spectra
        LOGGER.debug(f"Extracting indices for MS Levels: {self.mslevel}")
        self.mzmlData.get_target_ms_level_indices()

        # Get RT of spectra
        LOGGER.debug(f"Extracting RT values across spectra")
        self.mzmlData.get_spectra_rt_list()
        LOGGER.debug(f"RT Range: {self.mzmlData.meta_rt_list.min()} - {self.mzmlData.meta_rt_list.max()}")


        # Initialize empty MSExperiment container to store filtered data
        filtered = po.MSExperiment()
        pbar = tqdm(self.peptides.keys())
        pbar_desc = "INFO: Processing"
        for target_peptide_group in pbar:
            # Update progess bar description
            pbar_desc = f"INFO: Processing..{target_peptide_group}"
            pbar.set_description(pbar_desc)

            # Get Coordinates for current peptide
            target_peptide = self.peptides[target_peptide_group]['peptide']
            target_precursor_mz = self.peptides[target_peptide_group]['precursor_mz']
            target_product_mz = np.unique(self.peptides[target_peptide_group]['product_mz'])
            rt_apex = self.peptides[target_peptide_group]['rt_apex']
            im_apex = self.peptides[target_peptide_group]['im_apex']

            # Get tolerance bounds on coordinates
            target_precursor_mz_lower, target_precursor_mz_upper = self.get_upper_lower_tol(target_precursor_mz, self.ms1_mz_tol)
            target_product_upper_lower_list = [self.get_upper_lower_tol(mz, self.mz_tol) for mz in target_product_mz]

            rt_start, rt_end = self.get_rt_upper_lower(rt_apex)
            im_start, im_end = self.get_im_upper_lower(im_apex)

            LOGGER.debug(
                f"Extracting data for {target_peptide_group} | target precursor: {target_precursor_mz} m/z ({target_precursor_mz_lower} - {target_precursor_mz_upper}) | RT: {rt_apex} sec ({rt_start} - {rt_end}) | IM: {im_apex} 1/Ko ({im_start} - {im_end})")

            # Restrict spectra list further for RT window, to reduce the number of spectra we need to check to perform filtering on
            use_rt_spec_indices = np.where(np.array(
                [spec_rt >= rt_start and spec_rt <= rt_end for spec_rt in self.mzmlData.meta_rt_list]))
            target_spectra_indices = np.intersect1d(
                self.mzmlData.mslevel_indices, use_rt_spec_indices)

            with code_block_timer(f"Filtering {target_spectra_indices.shape[0]} Spectra for {target_peptide_group}...", LOGGER.debug):
                try:
                    filt_spec_list = Parallel(n_jobs=1)(delayed(self.filter_single_spectrum)(spectrum_indice, self.mslevel, target_peptide_group, im_start, im_end, target_precursor_mz, target_precursor_mz_lower, target_precursor_mz_upper, target_product_upper_lower_list) for spectrum_indice in target_spectra_indices.tolist())
                except:
                    traceback.print_exc(file=sys.stdout)

            # Add filtered spectra to MSExperiment container
            filt_spec_list = list(
                filter(lambda spectra: spectra is not None, filt_spec_list))
            # Add filtered spectrum to filtered MSExperiment container
            _ = [filtered.addSpectrum(spec) for spec in filt_spec_list]

        self.filtered = filtered

    @method_timer
    def get_df(self, ms_level: List[int]=[1]) -> pd.DataFrame:
        """
        Convert filtered spectra to Pandas DataFrame

        Args:
            self: (object) self object that contains filtered data
            ms_level: (list) list of ms level data to filter for
          
        Return:
            Pandas DataFrame of the filtered spectra
        """

        results_df = pd.DataFrame()
        for k in tqdm(range(self.filtered.getNrSpectra())):
            spec = self.filtered.getSpectrum(k)
            if spec.getMSLevel() in ms_level:
                mz, intensity = spec.get_peaks()
                if (len(mz) == 0 and len(intensity) == 0):
                    LOGGER.warn(
                        f"MS{spec.getMSLevel()} spectrum native id {spec.getNativeID()} had no m/z or intensity array, skipping this spectrum")
                    continue
                rt = np.full([mz.shape[0]], spec.getRT(), float)
                
                if not self.mzmlData.has_im:
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