import statistics
import numpy as np
import streamlit as st

def pad_data(data, max_length):
    """
    Pad the input data to a specified maximum length with zeros and a linear ramp.

    Args:
        data (list): A list containing two arrays, where data[0] is an array of retention times (Rt)
                     and data[1] is an array of intensities.
        max_length (int): The desired maximum length for the padded data.

    Returns:
        list: A list containing two arrays, the first padded with a linear ramp of retention times
              and the second padded with zeros to match the specified maximum length.

    If the length of the input data[0] is already greater than or equal to max_length, the
    function returns the original data without modification.
    """
    if len(data) < max_length:
        pad_width = max_length - len(data)
        # Pad Intensity array with 0 at the end
        padded_intensity = np.pad(data[1], (0, pad_width), 'constant', constant_values=0)
        # Pad Rt array with a linear ramp at the end
        last_rt_value = data[0][-1]
        second_last_rt_value = data[0][-2]
        rt_difference = last_rt_value - second_last_rt_value
        padded_rt = np.pad(data[0], (0, pad_width), 'linear_ramp', end_values=(last_rt_value, last_rt_value + rt_difference))
        return [list(padded_rt), list(padded_intensity)]
    else:
        return data

def get_max_rt_array_length(chrom_data, include_ms1=True, include_ms2=True):
    """
    Get the maximum length of RT arrays in the given `chrom_data` dictionary.

    Args:
        chrom_data (dict): A dictionary containing chromatogram data.
        include_ms1 (bool, optional): Whether to include MS1 data in the calculation.
            Defaults to True.
        include_ms2 (bool, optional): Whether to include MS2 data in the calculation.
            Defaults to True.

    Returns:
        int: The maximum length of RT arrays in the chromatogram data.
    """
    max_rt_array = 0

    for sqmass_file_data in chrom_data.values():
        if include_ms1:
            ms1_data = sqmass_file_data.get('ms1')
            if ms1_data:
                max_rt_array = max(max_rt_array, len(ms1_data[0]))

        if include_ms2:
            ms2_data = sqmass_file_data.get('ms2')
            if ms2_data:
                for chrom in ms2_data[0]:
                    max_rt_array = max(max_rt_array, len(chrom[0]))

    return max_rt_array

def normalize(intensity):
    """
    Normalize the input intensity array using min-max scaling.

    Args:
        intensity (list): An array of intensity values.

    Returns:
        list: A new array where each intensity value is scaled to the range [0, 1] using min-max scaling.
              If the input array is all zeros (no variation), it is returned unchanged.

    Min-max scaling is applied to the input intensity array by rescaling each value to fall within the
    range [0, 1] based on the minimum and maximum intensity values in the original array. If the input
    array is all zeros, indicating no variation, it is returned as is, as normalization is not applicable.

    Example:
    >>> intensity = [100, 50, 150, 75]
    >>> normalized_intensity = normalize(intensity)
    >>> print(normalized_intensity)
    [0.5, 0.0, 1.0, 0.25]
    """
    if not np.any(intensity): # if array is all 0s no normalization is done
        return intensity
    else:
        print("Info: Performing min-max scaling")
        return [(x - min(intensity)) / (max(intensity) - min(intensity)) for x in intensity]

def average_chromatograms(chrom_data, scale_intensity=False):
    """
    Average chromatograms.

    Args:
        chrom_data (list): List of chromatogram data.
        scale_intensity (bool): If True, perform min-max scaling on intensity values (default is False).

    Returns:
        list: List of data including the chosen RT and averaged Intensity.
    """
    # Find the maximum length among all sublists
    max_length = max(len(sublist[1]) for sublist in chrom_data)
    
    # Initialize variables to store the sum of Intensity
    sum_int = [0.0] * max_length
    max_length_rt = None

    # Calculate the sum of Intensity, taking care of varying sublist lengths
    num_samples = len(chrom_data)
    for sample in chrom_data:
        rt, intensity = sample[0], sample[1]
        if len(intensity) < max_length:
            # Pad the intensity with zeros to match max_length
            intensity += [0.0] * (max_length - len(intensity))
        if scale_intensity:
            intensity = normalize(intensity)
        for i in range(max_length):
            sum_int[i] += intensity[i]
        if len(rt) == max_length:
            max_length_rt = rt

    # Calculate the average Intensity
    average_int = [intensity / num_samples for intensity in sum_int]

    # Combine RT and Intensity into a single list
    result = [[max_length_rt, average_int]]

    return result

def median_chromatograms(chrom_data, scale_intensity=False):
    """
    Compute the median of chromatograms.

    Args:
        chrom_data (list): List of chromatogram data.
        scale_intensity (bool): If True, perform min-max scaling on intensity values (default is False).

    Returns:
        list: List of data including the chosen RT and median Intensity.
    """
    # Find the maximum length among all sublists
    max_length = max(len(sublist[1]) for sublist in chrom_data)

    # Initialize variables to store the list of Intensity values
    intensity_values = [[] for _ in range(max_length)]
    max_length_rt = None

    # Collect Intensity values, taking care of varying sublist lengths
    for sample in chrom_data:
        rt, intensity = sample[0], sample[1]
        if len(intensity) < max_length:
            # Pad the intensity with zeros to match max_length
            intensity += [0.0] * (max_length - len(intensity))
        if scale_intensity:
            # Perform min-max scaling
            intensity = [(x - min(intensity)) / (max(intensity) - min(intensity)) for x in intensity]
        for i in range(max_length):
            intensity_values[i].append(intensity[i])
        if len(rt) == max_length:
            max_length_rt = rt

    # Calculate the median Intensity for each position
    median_int = [statistics.median(values) for values in intensity_values]

    # Combine RT and Intensity into a single list
    result = [[max_length_rt, median_int]]

    return result

def percentile_average_chromatograms(chrom_data, percentile_start=10, percentile_end=90, threshold=0, scale_intensity=False):
    """
    Compute the percentile-averaged chromatograms.

    Args:
        chrom_data (list): List of chromatogram data.
        percentile_start (int): The start percentile for averaging (default is 10).
        percentile_end (int): The end percentile for averaging (default is 90).
        threshold (float): Intensity values below this threshold will be excluded from averaging (default is 0).
        scale_intensity (bool): If True, perform min-max scaling on intensity values (default is False).

    Returns:
        list: List of data including the chosen RT and percentile-averaged Intensity.
    """
    # Find the maximum length among all sublists
    max_length = max(len(sublist[1]) for sublist in chrom_data)

    # Initialize variables to store the list of Intensity values
    intensity_values = [[] for _ in range(max_length)]
    max_length_rt = None

    # Collect Intensity values, taking care of varying sublist lengths
    for sample in chrom_data:
        rt, intensity = sample[0], sample[1]
        if len(intensity) < max_length:
            # Pad the intensity with zeros to match max_length
            intensity += [0.0] * (max_length - len(intensity))
        if scale_intensity:
            # Perform min-max scaling
            intensity = normalize(intensity)
        for i in range(max_length):
            if intensity[i] > threshold:
                intensity_values[i].append(intensity[i])
        if len(rt) == max_length:
            max_length_rt = rt

    # Calculate the percentile-averaged Intensity for each position
    lower_percentile = max(0, percentile_start)
    upper_percentile = min(100, percentile_end)
    percentile_int = [np.percentile(values, lower_percentile) if values else 0.0 for values in intensity_values]

    # Combine RT and Intensity into a single list
    result = [[max_length_rt, percentile_int]]

    return result

def compute_threshold(chrom_data, percentile_threshold=10):
    """
    Calculate thresholds for a list of chromatogram data based on a specified percentile.

    Parameters:
    - chrom_data (list of tuples): A list of chromatogram data, where each element is a tuple.
                                  Each tuple should contain (time, intensity) data.
    - percentile_threshold (int or float, optional): The desired percentile for threshold calculation.
                                                     Defaults to 10 if not specified.

    Returns:
    - thresholds (list of float): A list of threshold values corresponding to the specified percentile
                                  for each chromatogram data in chrom_data.
    """
    thresholds = []

    for sub_data in chrom_data:
        # Extract intensity values from each sub_data
        intensity_values = sub_data[1]

        # Compute the threshold based on the desired percentile
        threshold = np.percentile(intensity_values, percentile_threshold)
        thresholds.append(threshold)
    print(f"auto-thresholds: {np.median(thresholds)}")
    return np.median(thresholds)

# @st.cache_data
def compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, auto_threshold=False):
    """
    Compute a consensus chromatogram based on the specified mode.

    Parameters:
    - consensus_chrom_mode (str): The mode for computing the consensus chromatogram ('averaged', 'median', or 'percentile_average').
    - chrom_data_all (list): List of chromatogram data.
    - scale_intensity (bool): Whether to scale the intensity.
    - percentile_start (int): The start percentile for 'percentile_average' mode.
    - percentile_end (int): The end percentile for 'percentile_average' mode.
    - auto_threshold (bool, optional): Whether to automatically compute the threshold for 'percentile_average' mode.

    Returns:
    - averaged_chrom_data: The computed consensus chromatogram.
    """
    if consensus_chrom_mode == 'averaged':
        averaged_chrom_data = average_chromatograms(chrom_data_all, scale_intensity)
    elif consensus_chrom_mode == 'median':
        averaged_chrom_data = median_chromatograms(chrom_data_all, scale_intensity)
    elif consensus_chrom_mode == 'percentile_average':
        if auto_threshold:
            threshold = compute_threshold(chrom_data_all, percentile_start)
        else:
            threshold = None
        averaged_chrom_data = percentile_average_chromatograms(chrom_data_all, percentile_start, percentile_end, threshold, scale_intensity)
    print(f"Info: returning consensus chromatogram: len(rt) : {len(averaged_chrom_data[0][0])} and len(ints): {len(averaged_chrom_data[0][1])}")
    return averaged_chrom_data

