import pyopenms as po
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature
from typing import List

class MRMTransitionGroupPicker:
    ''' python wrapper of the pyopenms MRMTransitionGroupPicker '''

    def __init__(self, smoother, **kwargs):
        ' smoother - which smoother to use for picking chromatogram valid options: ["original", "guassian", "sgolay"]'
        ' **kwargs - keyword arguments to be passed to setSmoother function valid options ["sgolay_frame_length (default 11)", "sgolay_polynomial_order (default 3)", "gauss_width (default 50.0)"]'
        self.picker = po.MRMTransitionGroupPicker()
        self.params = self.setDefaults()
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

        self.picker.setParameters(self.params)


    def setGeneralParameters(self, param, value):
        ''' Set a supported parameter '''
        valid_params = ['stop_after_feature', 'stop_after_intensity_ratio', 'min_peak_width', 'use_consensus', 'recalculate_peaks_max_z']
        if param not in valid_params:
            raise ValueError("Parameter is not valid or is not currently supported")
        else:
            self.params.setValue(bytes(param), value)
            self.picker.setParameters(self.params)

    def pick(self, transitionGroup: TransitionGroup) -> List[PeakFeature]:
        ''' Performs Peak Picking, Should return a PeakFeatureList object '''
        pyopenmsTransitionGroup = transitionGroup.to_pyopenms()
        pyopenmsFeatures = self.picker.pickTransitionGroup(pyopenmsTransitionGroup).getFeatures()
        return self._convertPyopenMSFeaturesToPeakFeatures(pyopenmsFeatures)

    def _convertPyopenMSFeaturesToPeakFeatures(self, pyopenmsFeatures) -> List[PeakFeature]:
        ''' Convert pyopenms features to PeakFeatures '''
        peakFeatures = []
        for f in pyopenmsFeatures:
            peakFeatures.append(PeakFeature(leftWidth=f.getMetaValue(b'leftWidth'), 
                                            rightWidth=f.getMetaValue(b'rightWidth'),
                                            area_intensity=f.getIntensity(),
                                            apex=f.getRT()))
        return peakFeatures