from massseer.peakPickers.GenericPeakPicker import GenericPeakPicker
import pyopenms as po
import numpy as np
from massseer.structs.Chromatogram import Chromatogram
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.structs.TransitionFeature import TransitionFeature
from massseer.structs.TransitionGroup import TransitionGroup
from typing import List

class pyMRMTransitionGroupPicker:
    '''
    This is a python implementation based on OpenMS peak picker
    '''

    def __init__(self, level='ms1ms2', sgolay_frame_length=11, sgolay_polynomial_order=3, merged_peak_picking=False):
        self.level = level
        self.top_n_features = 5
        self.peak_picker = po.PeakPickerMRM()
        

        ##### Set the pyopenms peak picker parameters
        params = self.peak_picker.getDefaults()
        params.setValue(b'sgolay_frame_length', sgolay_frame_length)
        params.setValue(b'sgolay_polynomial_order', sgolay_polynomial_order)
        params.setValue(b'use_gauss', 'false')
        params.setValue(b'method', 'corrected')
        self.peak_picker.setParameters(params)

    def _resolveLevel(self, transitionGroup):
        if self.level == 'ms1':
            chroms = transitionGroup.precursorChroms
        elif self.level == 'ms2':
            chroms = transitionGroup.transitionChroms
        elif self.level == 'ms1ms2':
            chroms = transitionGroup.precursorChroms + transitionGroup.transitionChroms
        else:
            raise ValueError(f"level must be one of ['ms1', 'ms2', 'ms1ms2'], not {self.level}")
        return chroms


    def find_peak_boundaries(self, chrom: Chromatogram) -> List[TransitionFeature]:
        """
        Find peak boundaries using the PeakPickerMRM algorithm.

        Args:
            rt_arr (np.array): Array of retention times.
            rt_acc_im (np.array): Array of accumulated intensities.

        Returns:
            dict: A dictionary containing the FWHM, integrated intensity, left width, and right width for each peak,
                with keys corresponding to the names of the data arrays.
        """

        # Create an MSChromatogram object
        po_chrom = chrom.topyopenms()

        # Create an empty MSChromatogram object to store the picked chromatogram
        picked_chrom = po.MSChromatogram()

        self.peak_picker.pickChromatogram(po_chrom, picked_chrom)

        # Extract the peak boundaries from the picked chromatogram and store them in a dictionary
        transitionFeatures = []
        if len(picked_chrom.get_peaks()[0]) > 0: ## return nothing if no peaks found
            apex_arr, apex_intensity_arr = picked_chrom.get_peaks()
            fda = p.getFloatDataArrays()
            area_intensity_arr = fda[1].get_data()
            left_boundary_arr = fda[2].get_data()
            right_boundary_arr = fda[3].get_data()

            for apex, apex_intensity, area_intensity, left_boundary, right_boundary in zip(apex_arr, apex_intensity_arr, area_intensity_arr, left_boundary_arr, right_boundary_arr):
                    transitionFeatures.append(TransitionFeature(left_boundary, right_boundary, area_intensity=area_intensity, peak_apex=apex, peak_apex_intensity=apex_intensity))
        return transitionFeatures

    def get_peak_boundariers_for_single_chromatogram(self, chrom: Chromatogram ) -> List[TransitionGroupFeature]:
        """
        Get peak boundaries for a single chromatogram.

        Args:
            chrom_data (list): List of chromatogram data.
            rt_peak_picker (pyopenms.PeakPickerMRM): PeakPickerMRM object.
            top_n_features (int): Number of top features to consider for merging (default is None).

        Returns:
            dict: A dictionary containing the consensus peak boundaries and integrated intensity.
        """
        peak_features = self.find_peak_boundaries(chrom)

        if peak_features is not None:
            merged_intensities = []
            for boundary in zip(peak_features.getBoundaries()):
                integrated_intensity = chrom.calculate_highest_intensity(boundary)
                merged_intensities.append(integrated_intensity)

            # Convert peak boundaries to a list of tuples
            merged_boundaries = [i.getBoundaries() for i in peak_features ] 

            # Sort the merged boundaries by integrated intensity in descending order
            sorted_boundaries = sorted(zip(merged_boundaries, merged_intensities), key=lambda x: x[1], reverse=True)

        # Filter the top n features if specified
        if self.top_n_features is not None:
            sorted_boundaries = sorted_boundaries[:self.top_n_features]

        top_boundaries, top_intensities = zip(*sorted_boundaries)

        # Calculate the consensus boundaries and integrated intensity
        transitionGroupFeatures = []
        for boundary, intensity in zip(top_boundaries, top_intensities):
            leftBoundary, rightBoundary = boundary
            transitionGroupFeatures.append(TransitionGroupFeature(leftBoundary, rightBoundary, area_intensity=intensity)) 
        return transitionGroupFeatures

    def merge_and_calculate_consensus_peak_boundaries(self, transitionGroup):
        """
        Merge peak boundaries from multiple chromatograms and calculate the consensus peak boundaries and integrated intensity.

        Args:
            chrom_data (list): List of chromatogram data.
            rt_peak_picker (pyopenms.PeakPickerMRM): PeakPickerMRM object.
            top_n_features (int): Number of top features to consider for merging (default is None).

        Returns:
            dict: A dictionary containing the consensus peak boundaries and integrated intensity.
        """
        chroms = self._resolveLevel(transitionGroup)
        trace_peaks_list = []
        # Iterate through chrom_data to find peak boundaries
        min_rt, max_rt = None, None
        for i in range(len(chroms)):
            if min_rt is None or min_rt > min(chroms[i].rt):
                min_rt = min(chroms[i].rt)
            if max_rt is None or max_rt > max(chroms[i].rt):
                max_rt = max(chroms[i].rt)
            peak_features = self.find_peak_boundaries(chroms[i])
            if peak_features is not None:
                trace_peaks_list.append(peak_features)
        if len(trace_peaks_list)==0:
            return TransitionGroupFeature(leftWidth=min_rt, rightWidth=max_rt, IntegratedIntensity=0)

        # Initialize empty lists to store boundaries and intensities
        boundaries = []
        integrated_intensities = []

        # Iterate through the dictionaries in the list
        for trace_peak_dict in trace_peaks_list:
            integrated_intensity = trace_peak_dict['IntegratedIntensity']

            # Combine left and right boundaries
            peak_boundaries = [ i.getBoundaries for i in peak_features ]

            # Append boundaries and integrated intensity
            boundaries.extend(peak_boundaries)
            integrated_intensities.extend(integrated_intensity)

        # Sort boundaries by their left end
        boundaries.sort(key=lambda x: x[0])

        # Initialize the merged boundaries and intensities
        merged_boundaries = [boundaries[0]]
        merged_intensities = [integrated_intensities[0]]

        # Merge overlapping boundaries and accumulate intensities
        for i in range(1, len(boundaries)):
            # print(f"Adding {boundaries[i]}")
            if boundaries[i][0] < merged_boundaries[-1][1]:
                if boundaries[i][1] > merged_boundaries[-1][1]:
                    # Overlapping boundaries; merge them
                    merged_boundaries[-1] = (merged_boundaries[-1][0], boundaries[i][1])
                # Accumulate intensities
                merged_intensities[-1] += integrated_intensities[i]
            else:
                # print(f"Appending Non-Overlapping {boundaries[i]}")
                # Non-overlapping boundaries; append them
                merged_boundaries.append(boundaries[i])
                merged_intensities.append(integrated_intensities[i])


        # Recompute the integrated intensities for merged boundaries
        merged_intensities = []
        for merged_boundary in list(merged_boundaries):
            # Find data points within the merged boundary range and compute integrated intensity
            integrated_intensity = chroms.calculate_highest_intensity(merged_boundary)
            merged_intensities.append(integrated_intensity)

        # Sort the merged boundaries by integrated intensity in descending order
        sorted_boundaries = sorted(zip(merged_boundaries, merged_intensities), key=lambda x: x[1], reverse=True)

        # Filter the top n features if specified
        if self.top_n_features is not None:
            sorted_boundaries = sorted_boundaries[:self.top_n_features]

        top_boundaries, top_intensities = zip(*sorted_boundaries)

        # Calculate the consensus boundaries and integrated intensity
        transitionGroupFeatures = []
        for boundary, intensity in zip(top_boundaries, top_intensities):
            leftBoundary, rightBoundary = boundary
            transitionGroupFeatures.append(TransitionGroupFeature(leftBoundary, rightBoundary, area_intensity=intensity)) 
        
        return transitionGroupFeatures

    def pick(self, transitionGroup: TransitionGroup) -> List[TransitionGroupFeature]:
        if self.merged_peak_picking:
            peak_features = self.merge_and_calculate_consensus_peak_boundaries(transitionGroup)
        else:
            peak_features = self.get_peak_boundariers_for_single_chromatogram(transitionGroup)

        return peak_features
