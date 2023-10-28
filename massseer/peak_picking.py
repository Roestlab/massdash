import pyopenms as po
import numpy as np


def calculate_integrated_intensity(chrom_data, boundary):
    """
    Calculates the integrated intensity of a chromatogram within a given boundary.

    Args:
        chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
        boundary (tuple): A tuple containing the left and right boundaries of the integration range.

    Returns:
        float: The integrated intensity of the chromatogram within the given boundary.
    """
    if isinstance(boundary, tuple):
        left, right = boundary
        integrated_intensity = 0.0
        for chrom in chrom_data:
            for rt, int in zip(chrom[0], chrom[1]):
                # Check if each data point is within the range of the current boundary
                # print(f"left: {left}, right: {right}, rt: {rt}")
                if left <= rt <= right:
                    integrated_intensity += int  # Access intensity using the correct index
    else:
        # Handle non-tuple boundaries here if needed
        pass
    return integrated_intensity

def calculate_median_intensity(chrom_data, boundary):
    """
    Calculate the median intensity of a given boundary in the chromatogram data.

    Args:
        chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
        boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

    Returns:
        float: The median intensity value of the data points within the given boundary.
    """
    if isinstance(boundary, tuple):
        left, right = boundary
        intensity_values = []

        for chrom in chrom_data:
            for rt, int in zip(chrom[0], chrom[1]):
                # Check if each data point is within the range of the current boundary
                # print(f"left: {left}, right: {right}, rt: {rt}")
                if left <= rt <= right:
                    intensity_values.append(int)  

        # Calculate the median intensity
        median_intensity = np.median(intensity_values)
    else:
        # Handle non-tuple boundaries here if needed
        pass

    return median_intensity

def calculate_highest_intensity(chrom_data, boundary):
    """
    Calculate the highest intensity within a given boundary.

    Args:
        chrom_data (list): A list of tuples containing chromatogram data.
        boundary (tuple): A tuple containing the left and right boundaries.

    Returns:
        float: The highest intensity within the given boundary.
    """
    if isinstance(boundary, tuple):
        left, right = boundary
        highest_intensity = 0.0  # Initialize with a default value
        for chrom in chrom_data:
            for rt, int in zip(chrom[0], chrom[1]):
                # Check if each data point is within the range of the current boundary
                if left <= rt <= right:
                    highest_intensity = max(highest_intensity, int)  

    else:
        # Handle non-tuple boundaries here if needed
        pass

    return highest_intensity

def find_peak_boundaries(rt_arr, rt_acc_im, peak_picker):
      """
      Find peak boundaries using the PeakPickerMRM algorithm.

      Args:
          rt_arr (np.array): Array of retention times.
          rt_acc_im (np.array): Array of accumulated intensities.
          peak_picker (pyopenms.PeakPickerMRM): PeakPickerMRM object.

      Returns:
          dict: A dictionary containing the FWHM, integrated intensity, left width, and right width for each peak,
              with keys corresponding to the names of the data arrays.
      """
    #   print(f"len(rt_arr): {len(rt_arr)} and len(rt_acc_im): {len(rt_acc_im)}")
    #   print(rt_arr)
    #   print(rt_acc_im)
      # Create an MSChromatogram object
      chrom = po.MSChromatogram()
      chrom.set_peaks([rt_arr, rt_acc_im])

      # Create an empty MSChromatogram object to store the picked chromatogram
      picked_chrom = po.MSChromatogram()

      peak_picker.pickChromatogram(chrom, picked_chrom)

      # Extract the peak boundaries from the picked chromatogram and store them in a dictionary
      if len(picked_chrom.get_peaks()[0]) > 0: ## return nothing if no peaks found
          peak_boundaries = {}
          float_data_arrays = picked_chrom.getFloatDataArrays()
          for i in range(len(float_data_arrays)):
              fda = float_data_arrays[i]
              name = fda.getName()
              value = fda.get_data().copy()
              # print(f"{name}: {value}")
              peak_boundaries[name] = value

          peak_boundaries['ApexRT'] = picked_chrom.get_peaks()[0]
          peak_boundaries['ApexIntensity'] = picked_chrom.get_peaks()[1]

          return peak_boundaries
      else:
          return None

def get_peak_boundariers_for_single_chromatogram(chrom_data, rt_peak_picker, top_n_features=5):
    """
    Get peak boundaries for a single chromatogram.

    Args:
        chrom_data (list): List of chromatogram data.
        rt_peak_picker (pyopenms.PeakPickerMRM): PeakPickerMRM object.
        top_n_features (int): Number of top features to consider for merging (default is None).

    Returns:
        dict: A dictionary containing the consensus peak boundaries and integrated intensity.
    """
    peak_features = find_peak_boundaries(chrom_data[0], chrom_data[1], rt_peak_picker)

    if peak_features is not None:
        merged_intensities = []
        for boundary in zip(peak_features['leftWidth'], peak_features['rightWidth']):
            integrated_intensity = calculate_highest_intensity([chrom_data], boundary)
            merged_intensities.append(integrated_intensity)

        # Convert peak boundaries to a list of tuples
        merged_boundaries = [(left, right) for left, right in zip(peak_features['leftWidth'], peak_features['rightWidth'])]

        # Sort the merged boundaries by integrated intensity in descending order
        sorted_boundaries = sorted(zip(merged_boundaries, merged_intensities), key=lambda x: x[1], reverse=True)

        # Filter the top n features if specified
        if top_n_features is not None:
            sorted_boundaries = sorted_boundaries[:top_n_features]

        top_boundaries, top_intensities = zip(*sorted_boundaries)

        # Calculate the consensus boundaries and integrated intensity
        consensus_left_widths, consensus_right_widths = zip(*top_boundaries)
        consensus_dict = {
            'leftWidth': consensus_left_widths,
            'rightWidth': consensus_right_widths,
            'IntegratedIntensity': top_intensities
        }
        # print(f"Top Consensus Peaks: {consensus_dict}")

        return consensus_dict
    else:
        return None

def merge_and_calculate_consensus_peak_boundaries(chrom_data, rt_peak_picker, top_n_features=5):
    """
    Merge peak boundaries from multiple chromatograms and calculate the consensus peak boundaries and integrated intensity.

    Args:
        chrom_data (list): List of chromatogram data.
        rt_peak_picker (pyopenms.PeakPickerMRM): PeakPickerMRM object.
        top_n_features (int): Number of top features to consider for merging (default is None).

    Returns:
        dict: A dictionary containing the consensus peak boundaries and integrated intensity.
    """
    trace_peaks_list = []

    # Iterate through chrom_data to find peak boundaries
    for i in range(len(chrom_data)):
        # print(f" i = {i} and len(chrom_data[i][0]) = {len(chrom_data[i][0])} and len (chrom_data[i][0]) = {len(chrom_data[i][0])}")
        # print(f"chrom_data[i][0]: {chrom_data[i][0]}")
        # print(f"chrom_data[i][1]: {chrom_data[i][1]}")
        peak_features = find_peak_boundaries(chrom_data[i][0], chrom_data[i][1], rt_peak_picker)
        if peak_features is not None:
            trace_peaks_list.append(peak_features)

    # Initialize empty lists to store boundaries and intensities
    boundaries = []
    integrated_intensities = []

    # Iterate through the dictionaries in the list
    for trace_peak_dict in trace_peaks_list:
        left_widths = trace_peak_dict['leftWidth']
        right_widths = trace_peak_dict['rightWidth']
        integrated_intensity = trace_peak_dict['IntegratedIntensity']

        # Combine left and right boundaries
        peak_boundaries = list(zip(left_widths, right_widths))

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
        integrated_intensity = calculate_highest_intensity(chrom_data, merged_boundary)
        merged_intensities.append(integrated_intensity)

    # Sort the merged boundaries by integrated intensity in descending order
    sorted_boundaries = sorted(zip(merged_boundaries, merged_intensities), key=lambda x: x[1], reverse=True)

    # Filter the top n features if specified
    if top_n_features is not None:
        sorted_boundaries = sorted_boundaries[:top_n_features]

    top_boundaries, top_intensities = zip(*sorted_boundaries)

    # Calculate the consensus boundaries and integrated intensity
    consensus_left_widths, consensus_right_widths = zip(*top_boundaries)
    consensus_dict = {
        'leftWidth': consensus_left_widths,
        'rightWidth': consensus_right_widths,
        'IntegratedIntensity': top_intensities
    }
    # print(f"Top Consensus Peaks: {consensus_dict}")
    return consensus_dict

def perform_chromatogram_peak_picking(chrom_data_all, do_smoothing, smoothing_dict, merged_peak_picking=False):
    """
    Perform peak picking on a chromatogram using the specified parameters.

    Args:
        chrom_data_all (list): The chromatogram data.
        do_smoothing (bool): Whether to perform smoothingggg
        sgolay_frame_length (int): The frame length to use for Savitzky-Golay smoothing.
        sgolay_polynomial_order (int): The polynomial order to use for Savitzky-Golay smoothing.
        merged_peak_picking (bool, optional): Whether to perform merged peak picking. Defaults to False.

    Returns:
        dict: The peak features.
    """
    if merged_peak_picking:
        # Create a PeakPickerMRM object and use it to pick the peaks in the chromatogram
        rt_peak_picker = po.PeakPickerMRM()
        peak_picker_params = rt_peak_picker.getParameters()
        peak_picker_params.setValue(b'gauss_width', 30.0)
        peak_picker_params.setValue(b'use_gauss', 'false')
        peak_picker_params.setValue(b'sgolay_frame_length', smoothing_dict['sgolay_frame_length'] if do_smoothing == 'sgolay' else 11)
        peak_picker_params.setValue(b'sgolay_polynomial_order', smoothing_dict['sgolay_polynomial_order'] if do_smoothing == 'sgolay' else 3)
        peak_picker_params.setValue(b'remove_overlapping_peaks', 'true')
        rt_peak_picker.setParameters(peak_picker_params)
        peak_features = merge_and_calculate_consensus_peak_boundaries(chrom_data_all, rt_peak_picker)
    else:
        # Create a PeakPickerMRM object and use it to pick the peaks in the chromatogram
        rt_peak_picker = po.PeakPickerMRM()
        peak_picker_params = rt_peak_picker.getParameters()
        peak_picker_params.setValue(b'gauss_width', 30.0)
        peak_picker_params.setValue(b'use_gauss', 'false')
        peak_picker_params.setValue(b'sgolay_frame_length', smoothing_dict['sgolay_frame_length'] if do_smoothing == 'sgolay' else 11)
        peak_picker_params.setValue(b'sgolay_polynomial_order', smoothing_dict['sgolay_polynomial_order'] if do_smoothing == 'sgolay' else 3)
        peak_picker_params.setValue(b'remove_overlapping_peaks', 'true')
        rt_peak_picker.setParameters(peak_picker_params)
        peak_features = get_peak_boundariers_for_single_chromatogram(chrom_data_all, rt_peak_picker)

    return peak_features