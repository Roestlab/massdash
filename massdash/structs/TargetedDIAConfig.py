"""
massdash/structs/TargetedDIAConfig
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Tuple, List

class TargetedDIAConfig:
    """
    A class representing the configuration for the extraction windows.

    Attributes:
        ms1_mz_tol (float): The m/z tolerance for MS1 spectra.
        mz_tol (float): The m/z tolerance for MS2 spectra.
        rt_window (float): The retention time window for spectra.
        im_window (float): The ion mobility window for spectra.
        mslevel (list): A list of MS levels to include.
        
    Methods:
        update: Update the configuration attributes using a dictionary.
    """
    def __init__(self):
        self._ms1_mz_tol = 20
        self._mz_tol = 20
        self._rt_window = 50
        self._im_window = 0.06
        self._mslevel = [1, 2]
        self._im_start= None
        self._im_end = None

    # Define properties with custom setters for each attribute
    @property
    def ms1_mz_tol(self):
        return self._ms1_mz_tol

    @ms1_mz_tol.setter
    def ms1_mz_tol(self, value):
        self._ms1_mz_tol = value

    @property
    def mz_tol(self):
        return self._mz_tol

    @mz_tol.setter
    def mz_tol(self, value):
        self._mz_tol = value

    @property
    def rt_window(self):
        return self._rt_window

    @rt_window.setter
    def rt_window(self, value):
        self._rt_window = value

    @property
    def im_window(self):
        return self._im_window

    @im_window.setter
    def im_window(self, value):
        self._im_window = value

    @property
    def mslevel(self):
        return self._mslevel

    @mslevel.setter
    def mslevel(self, value):
        self._mslevel = value

    @property 
    def im_start(self):
        return self._im_start

    @im_start.setter
    def im_start(self, value):
        self._im_start = value

    @property 
    def im_end(self):
        return self._im_end

    @im_end.setter
    def im_end(self, value):
       self._im_end = value

    def __str__(self):
        return f"{'-'*8} {__class__.__name__} {'-'*8}\nms1_mz_tol: {self.ms1_mz_tol}\nmz_tol: {self.mz_tol}\nrt_window: {self.rt_window}\nim_window: {self.im_window}\nmslevel: {self.mslevel}"

    def update(self, config_dict):
        """
        Update the configuration attributes using a dictionary.

        Args:
            config_dict (dict): A dictionary containing configuration values.
        
        Example:
            config_dict = {
                'rt_window': 50,
                'im_window': 0.06,
                'mslevel': [1, 2]
            }
            config.update(config_dict)
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_upper_lower_tol(self, target_mz: float) -> Tuple[float, float]:
        """
        Get the upper bound and lower bound mz around a target mz given a mz tolerance in ppm

        Args:
          target_mz: (float) The target mz to generate upper and lower bound mz coordinates for
          mz_tol: (int) The m/z tolerance toget get upper and lower bounds arround target mz. Must be in ppm.

        Return: 
          (tuple) a tuple of the lower and upper bound for target mz
        """
        mz_uncertainty = target_mz * self.mz_tol / 2.0 * 1.0e-6
        target_precursor_mz_upper = target_mz + mz_uncertainty
        target_precursor_mz_lower = target_mz - mz_uncertainty
        return target_precursor_mz_lower, target_precursor_mz_upper

    def get_rt_upper_lower(self, rt_apex: float) -> Tuple[float, float]:
        """
        Get the upper bound and lower bound of a target RT point for a given RT window, i.e. a window of 50 would be 25 points to either side of the target RT.

        Args:
          rt_apex: (float) The target RT point to generate upper and lower bound RT coordinates for

        Return:
          (tuple) a tuple of the lower and upper bound for target RT
        """
        return rt_apex-(self.rt_window/2), rt_apex+(self.rt_window/2)

    def get_im_upper_lower(self, im_apex: float) -> Tuple[float, float]:
        """
        Get the upper bound and lower bound of a target IM point for a given IM window, i.e. a window of 0.06 would be 0.03 points to either side of the target IM.

        Args:
          im_apex: (float) The target IM point to generate upper and lower bound IM coordinates for

        Return:
          (tuple) a tuple of the lower and upper bound for target IM
        """
        if self.im_start is not None and self.im_end is not None:
            return (self.im_start, self.im_end)

        return im_apex-(self.im_window/2), im_apex+(self.im_window/2)

    def is_mz_in_product_mz_tol_window(self, check_mz: float, target_product_upper_lower_list: List[Tuple[float, float]]) -> bool:
        """
        Check to see if a target product ion mz is within upper and lower tolerance window

        Args: 
          check_mz: (float) The target product ion mz to check
          target_product_upper_lower_list: (list) A list of tuples that contain an upper and lower bound of a product mz

        Return: (bool) Return a logical value 
        """
        return any([check_mz >= bounds[0] and check_mz <= bounds[1] for bounds in target_product_upper_lower_list])
