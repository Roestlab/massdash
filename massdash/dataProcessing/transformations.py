"""
massdash/dataProcessing/transformations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np

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
        return [(x - min(intensity)) / (max(intensity) - min(intensity)) for x in intensity]
    
def equalize2D(arr: np.array, bins: int):
    """
    Equalize the input array using histogram equalization.

    Based off of http://www.janeriksolem.net/histogram-equalization-with-python-and.html

    Args:
        arr (np.array): An 2D array of intensity values.
        bins (int): The number of bins to use for the histogram.
    
    Returns:
        arr
    """
    # based on http://www.janeriksolem.net/histogram-equalization-with-python-and.html
    hist, bins = np.histogram(arr.flatten(), bins, density=True)
    cdf = hist.cumsum() # cumulative distribution function
    cdf = (bins - 1) * cdf / cdf[-1] # normalize

    # use linear interpolation of cdf to find new pixel values
    image_equalized = np.interp(arr.flatten(), bins[:-1], cdf)
    return  image_equalized.reshape(arr.shape)