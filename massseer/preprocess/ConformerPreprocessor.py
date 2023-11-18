import numpy as np

from massseer.preprocess.GenericPreprocessor import GenericPreprocessor 
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.chromatogram_data_handling import normalize


def min_max_scale(data, min=None, max=None):
    min = data.min() if not min else min
    max = data.max() if not max else max

    return np.nan_to_num((data - min) / (max - min))

class ConformerPreprocessor(GenericPreprocessor):
    def __init__(self, transition_group: TransitionGroup):
        super().__init__(transition_group)

    def preprocess(self):
        
        # Data array ordering:
            # Row index 0-5: ms2 (sample min-max normalized)
            # Row index 6-11: ms2 (trace min-max normalized)
            # Row index 12: ms1
            # Row index 13-18: library intensity
            # Row index 19: library retention time diff
            # Row index 20: precursor charge

        #  initialize empty numpy array
        data = np.empty((0, len(self.transition_group.transitionChroms[0].intensity)), float)

        lib_int_data = np.empty((0, len(self.transition_group.transitionChroms[0].intensity)), float)

        for chrom in self.transition_group.transitionChroms:
            # append ms2 intensity data to data
            data = np.append(data, [chrom.intensity], axis=0)

            lib_int =  self.transition_group.targeted_transition_list[self.transition_group.targeted_transition_list.Annotation==chrom.label]['LibraryIntensity'].values 
            lib_int = np.repeat(lib_int, len(chrom.intensity))
            lib_int_data = np.append(lib_int_data, [lib_int], axis=0)

        # initialize empty numpy array to store scaled data
        new_data = np.empty((21, len(self.transition_group.transitionChroms[0].intensity)), float)

        ## MS2 data (sample min-max normalized)
        new_data[0:6] = min_max_scale(data)

        ## MS2 trace data (trace min-max normalized)
        for j in range(6, 12):
            new_data[j : j + 1] = min_max_scale(
                data[j - 6 : j - 5]
            )

        ## MS1 trace data
        # padd precursor intensity data with zeros to match ms2 intensity data
        len_trans = len(self.transition_group.transitionChroms[0].intensity)
        len_prec = len(self.transition_group.precursorChroms[0].intensity)
        prec_int = np.pad(self.transition_group.precursorChroms[0].intensity, (0, len_trans-len_prec), 'constant', constant_values=(0, 0))
        # append ms1 intensity data to data
        new_data[12] = min_max_scale(prec_int)

        ## Library intensity data
        # append library intensity data to data
        new_data[13:19] = min_max_scale(lib_int_data)

        ## Library retention time diff
        # Find the middle index of the array
        middle_index = len(data[0]) // 2

        # Create a new array with the same length as the original_data
        tmp_arr = np.zeros_like(data[0], dtype=float)

        # Set the middle point to 0
        tmp_arr[middle_index] = 0

        # Increment by one on either side of the middle point
        for i in range(1, middle_index + 1):
            if middle_index - i >= 0:
                tmp_arr[middle_index - i] = i
            if middle_index + i < len(data[0]):
                tmp_arr[middle_index + i] = i

        new_data[19] = tmp_arr

        ## Add charge state
        new_data[20] = self.transition_group.targeted_transition_list.PrecursorCharge.values[0] * np.ones(len(data[0]))

        return new_data
