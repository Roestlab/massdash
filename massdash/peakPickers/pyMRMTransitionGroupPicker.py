from typing import List, Optional
import pandas as pd
import pyopenms as po

# Structs
from massdash.structs.Chromatogram import Chromatogram
from massdash.structs.TransitionGroupFeature import TransitionGroupFeature
from massdash.structs.TransitionFeature import TransitionFeature
from massdash.structs.TransitionGroup import TransitionGroup

class pyMRMTransitionGroupPicker:
    '''
    This is a python implementation based on OpenMS peak picker
    '''

    def __init__(self, level: str='ms1ms2', sgolay_frame_length: Optional[int]=11, sgolay_polynomial_order: Optional[int]=3, peak_picker: Optional[po.PeakPickerMRM]=None):
        self.level = level
        self.top_n_features = 5
        if peak_picker is None:
            self.peak_picker = po.PeakPickerMRM()
            ##### Set the pyopenms peak picker parameters
            params = self.peak_picker.getDefaults()
            params.setValue(b'sgolay_frame_length', sgolay_frame_length)
            params.setValue(b'sgolay_polynomial_order', sgolay_polynomial_order)
            params.setValue(b'use_gauss', 'false')
            params.setValue(b'method', 'corrected')
            params.setValue(b'remove_overlapping_peaks', 'true')
            self.peak_picker.setParameters(params)
        else:
            self.peak_picker = peak_picker

    def _resolveLevel(self, transitionGroup):
        if self.level == 'ms1':
            chroms = transitionGroup.precursorData
        elif self.level == 'ms2':
            chroms = transitionGroup.transitionData
        elif self.level == 'ms1ms2':
            chroms = transitionGroup.precursorData + transitionGroup.transitionData
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
        po_chrom = chrom.to_pyopenms()

        # Create an empty MSChromatogram object to store the picked chromatogram
        picked_chrom = po.MSChromatogram()

        self.peak_picker.pickChromatogram(po_chrom, picked_chrom)

        # Extract the peak boundaries from the picked chromatogram and store them in a dictionary
        transitionFeatures = []
        if len(picked_chrom.get_peaks()[0]) > 0: ## return nothing if no peaks found
            apex_arr, apex_intensity_arr = picked_chrom.get_peaks()
            fda = picked_chrom.getFloatDataArrays()
            area_intensity_arr = fda[1].get_data()
            left_boundary_arr = fda[2].get_data()
            right_boundary_arr = fda[3].get_data()

            for apex, apex_intensity, area_intensity, left_boundary, right_boundary in zip(apex_arr, apex_intensity_arr, area_intensity_arr, left_boundary_arr, right_boundary_arr):
                    transitionFeatures.append(TransitionFeature(left_boundary, right_boundary, areaIntensity=area_intensity, peakApex=apex, apexIntensity=apex_intensity))
        return transitionFeatures

    def pick(self, transitionGroup: TransitionGroup) -> List[TransitionGroupFeature]:
        """
        Performs Peak Picking, Should return a list of TransitionGroupFeatures
        """

        chroms = self._resolveLevel(transitionGroup)
        peaks = []
        # Iterate through chrom_data to find peak boundaries
        for c in range(len(chroms)):
            peaks.extend(self.find_peak_boundaries(chroms[c]))

        if len(peaks)==0:
            return []

        # Iterate through the dictionaries in the list
        peaksDf = TransitionFeature.toPandasDf(peaks)

        # sort boundaries by left end
        peaksDf.sort_values(by=['leftBoundary'], inplace=True)

        newPeaks = pd.DataFrame(peaksDf.loc[0]).T

        for idx in range(1, len(peaksDf)):
            if peaksDf['leftBoundary'].iloc[idx] < newPeaks['rightBoundary'].iloc[-1]:
                if peaksDf['rightBoundary'].iloc[idx] > peaksDf['rightBoundary'].iloc[-1]:
                    # Overlapping boundaries; merge them
                    newPeaks['rightBoundary'].iloc[-1] = peaksDf['rightBoundary'].iloc[idx]
                # Accumulate intensities
                newPeaks['areaIntensity'].iloc[-1] += peaksDf['areaIntensity'].iloc[idx]
            else:
                # Non-overlapping boundaries; append them
                newPeaks = pd.concat([newPeaks, peaksDf.iloc[[idx]]])

        # Recompute the peak apex for merged boundaries
        for idx in newPeaks.index:
            # Find data points within the merged boundary range and compute integrated intensity
            highest = (0,0)
            boundaries = tuple(newPeaks[['leftBoundary', 'rightBoundary']].loc[idx].values)
            for c in chroms:
                newHighest = c.max(boundaries)
                highest = highest if highest[1] > newHighest[1] else newHighest

            newPeaks.loc[idx, ['peakApex', 'apexIntensity']] = highest

        # Sort the merged boundaries by integrated intensity in descending order
        newPeaks.sort_values(by=['apexIntensity'], inplace=True, ascending=False)

        # Filter the top n features if specified
        if self.top_n_features is not None:
            newPeaks = newPeaks[:self.top_n_features]

        # Calculate the consensus boundaries and integrated intensity
        transitionGroupFeatures = []
        for idx, row in newPeaks.iterrows():
            transitionGroupFeatures.append(TransitionGroupFeature(row['leftBoundary'], row['rightBoundary'], areaIntensity=row['areaIntensity'], consensusApexIntensity=row['apexIntensity']))
        
        return transitionGroupFeatures