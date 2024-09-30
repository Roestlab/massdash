"""
massdash/peakPickers/MRMTransitionGroupPicker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pyopenms as po
from typing import List, Tuple

# Structs
from ..structs.TransitionGroup import TransitionGroup
from ..structs.TransitionGroupFeature import TransitionGroupFeature

class MRMTransitionGroupPicker:
    ''' python wrapper of the pyopenms MRMTransitionGroupPicker '''

    def __init__(self, smoother, **kwargs):
        ' smoother - which smoother to use for picking chromatogram valid options: ["original", "guassian", "sgolay"]'
        ' **kwargs - keyword arguments to be passed to setSmoother function valid options ["sgolay_frame_length (default 11)", "sgolay_polynomial_order (default 3)", "gauss_width (default 50.0)"]'
        self.picker = po.MRMTransitionGroupPicker()
        self.setDefaults()
        self.setSmoother(smoother, **kwargs)



    def setDefaults(self):
        ''' get the default parameters used by OpenSwath '''
        params = self.picker.getDefaults()

        params.setValue(b'stop_after_feature', -1)
        params.setValue( b'stop_after_intensity_ratio', 0.0001)
        params.setValue( b'min_peak_width', -1.0)
        params.setValue( b'peak_integration', 'original')
        params.setValue( b'background_subtraction', 'none')
        params.setValue( b'recalculate_peaks', 'true')
        params.setValue( b'use_precursors', 'false')
        params.setValue( b'use_consensus', 'true')
        params.setValue( b'recalculate_peaks_max_z', 0.75)
        params.setValue( b'minimal_quality', -10000.0)
        params.setValue( b'resample_boundary', 15.0)
        params.setValue( b'compute_peak_quality', 'false')
        params.setValue( b'compute_peak_shape_metrics', 'false')
        params.setValue( b'compute_total_mi', 'false')
        params.setValue( b'boundary_selection_method', 'largest')
        params.setValue( b'PeakPickerMRM:sgolay_frame_length', 11)
        params.setValue( b'PeakPickerMRM:sgolay_polynomial_order', 3)
        params.setValue( b'PeakPickerMRM:gauss_width', 50.0)
        params.setValue( b'PeakPickerMRM:use_gauss', 'false')
        params.setValue( b'PeakPickerMRM:peak_width', -1.0)
        params.setValue( b'PeakPickerMRM:signal_to_noise', 0.001)
        params.setValue( b'PeakPickerMRM:sn_win_len', 1000.0)
        params.setValue( b'PeakPickerMRM:sn_bin_count', 30)
        params.setValue( b'PeakPickerMRM:write_sn_log_messages', 'false')
        params.setValue( b'PeakPickerMRM:remove_overlapping_peaks', 'true')
        params.setValue( b'PeakPickerMRM:method', 'corrected')
        params.setValue( b'PeakIntegrator:integration_type', 'intensity_sum')
        params.setValue( b'PeakIntegrator:baseline_type', 'base_to_base')
        params.setValue( b'PeakIntegrator:fit_EMG', 'false')

        self.params = params
        self.picker.setParameters(params)


    def setSmoother(self, smoother, sgolay_frame_length=11, sgolay_polynomial_order=3, gauss_width=50.0):
        ''' Set the smoother, can be one of ["original", "guassian", "sgolay"] '''
        if smoother == 'original':
            self.params.setValue(b'PeakPickerMRM:method','legacy')
        elif smoother == 'gauss':
            self.params.setValue(b'PeakPickerMRM:method','corrected')
            self.params.setValue(b'PeakPickerMRM:use_gauss','true')
            self.params.setValue(b'PeakPickerMRM:gauss_width', gauss_width)
        elif smoother == 'sgolay':
            self.params.setValue(b'PeakPickerMRM:method','corrected')
            self.params.setValue(b'PeakPickerMRM:use_gauss','false')
            self.params.setValue(b'PeakPickerMRM:sgolay_frame_length', sgolay_frame_length)
            self.params.setValue(b'PeakPickerMRM:sgolay_polynomial_order', sgolay_polynomial_order)
        else:
            raise ValueError("Smoother must be one of ['original', 'gauss', 'sgolay']")

        self.picker.setParameters(self.params)


    def setGeneralParameters(self, **kwargs):
        ''' 
        Set a supported parameter

        Args:
            stop_after_feature (int): Stop after feature
            stop_after_intensity_ratio (float): Stop after intensity ratio
            min_peak_width (float): Minimum peak width
            recalculate_peaks_max_z (float): Recalculate peaks max z
            resample_boundary (float): Resample boundary
            recalculate_peaks (bool): Recalculate peaks
            background_subtraction (str): Background subtraction
            use_precursors (bool): Use precursors
            signal_to_noise (float): Signal to noise
            minimal_quality (float): Minimal quality (if set, automatically sets compute_peak_quality to true)
        '''

        valid_params = ['stop_after_feature', 'stop_after_intensity_ratio', 'min_peak_width', 'recalculate_peaks_max_z', 'resample_boundary', 'recalculate_peaks', 'background_subtraction', 'use_precursors', 'minimal_quality']
        mrmParams = ['signal_to_noise']
        bools_to_str = ['recalculate_peaks'] # these parameters require a "true" or "false" string
        valid_params = valid_params + mrmParams + bools_to_str
        for k, val in kwargs.items():
            if k not in valid_params:
                raise ValueError(f"Parameter {k} is not valid or is not currently supported")
            else:
                if k in mrmParams:
                    self.params.setValue(bytes('PeakPickerMRM:'+k, encoding='utf-8'), val)
                elif k in bools_to_str:
                    if k:
                        self.params.setValue(bytes(k, encoding='utf-8'), 'true')
                    else:
                        self.params.setValue(bytes(k, encoding='utf-8'), 'false')
                elif k == 'minimal_quality':
                    self.params.setValue(bytes(k, encoding='utf-8'), val)
                    self.params.setValue(bytes('compute_peak_quality', encoding='utf-8'), 'true')
                else:
                    self.params.setValue(bytes(k, encoding='utf-8'), val)
                self.picker.setParameters(self.params)

    def getPrettyParameters(self) -> Tuple:
        ''' 
        Get a list of current parameters and their values in a python friendly format
        Note: Changing the parameters will not update values
        '''
        return tuple(zip([ i.decode('utf-8') for i in self.params.keys()], self.params.values()))

    def pick(self, transitionGroup: TransitionGroup) -> List[TransitionGroupFeature]:
        ''' Performs Peak Picking, Should return a TransitionGroupFeatureList object '''
        pyopenmsTransitionGroup = transitionGroup.to_pyopenms()

        self.picker.pickTransitionGroup(pyopenmsTransitionGroup)
        pyopenmsFeatures = pyopenmsTransitionGroup.getFeatures()

        return self._convertPyopenMSFeaturesToTransitionGroupFeatures(pyopenmsFeatures)

    def _convertPyopenMSFeaturesToTransitionGroupFeatures(self, pyopenmsFeatures) -> List[TransitionGroupFeature]:
        ''' Convert pyopenms features to TransitionGroupFeatures '''
        transitionGroupFeatures = []
        for f in pyopenmsFeatures:
            transitionGroupFeatures.append(TransitionGroupFeature(leftBoundary=f.getMetaValue(b'leftWidth'), 
                                            rightBoundary=f.getMetaValue(b'rightWidth'),
                                            areaIntensity=f.getIntensity(),
                                            consensusApex=f.getRT()))
        return transitionGroupFeatures