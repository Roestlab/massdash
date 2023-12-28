import click

# data modules
import pyopenms as po
import numpy as np

# Server 
from massseer.server.util import check_ion_mobility
# Internal
from massseer.util import LOGGER, method_timer, code_block_timer

class mzMLDataAccess():
    """
    Class for data input and output operations
    
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

    def __init__(self, mzml_file, readOptions="ondisk", verbose=False):
        """
        Initialise mzMLDataAccess object

        Args:
          mzml_file: (str) mzML file to load
          readOptions: (str) readOptions to use, either 'ondisk' or 'cached'
          verbose (bool): Enables verbose mode.
        """
        
        self.filename = mzml_file
        self.readOptions = readOptions
        self.exp = po.OnDiscMSExperiment()
        self.meta_data = po.MSExperiment()
        self.has_im = check_ion_mobility(mzml_file)
        
        LOGGER.name = "mzMLDataAccess"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def __str__(self):
        return f"mzMLDataAccess(filename={self.filename}, has_im={self.has_im})"
 
    def __repr__(self):
        return f"mzMLDataAccess(filename={self.filename}, has_im={self.has_im})"

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
            
    def get_target_ms_level_indices(self, mslevel=[1,2]):
        """
        Extract spectrum indices for a specific mslevel(s).

        Args:
          self: (object) self object containing meta_data
        mslevel: (list) list of mslevel(s) to extract indices for

        Return:
          Return a list of indices with request mslevel(s) to self
        """
        if self.readOptions=="ondisk":
            spectra = self.meta_data.getSpectra()
            mslevel_indices = np.array([indice for indice, spec in enumerate(
                spectra) if spec.getMSLevel() in mslevel])
            self.mslevel_indices = mslevel_indices
        elif self.readOptions=="cached":
            self.mslevel_indices = np.array(range(0,self.exp.getNrSpectra()))
        else:
            click.ClickException(f"ERROR: Unknown readOptions ({self.readOptions}) given! Has to be one of 'ondisk', 'cached'")

    def get_spectra_rt_list(self):
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
