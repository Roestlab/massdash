import mmap

def get_string_mslevels_from_bool(mslevel_bool_dict):
    """
    Converts a dictionary of boolean values for mslevels to a string.

    Args:
    mslevel_bool_dict : dict
        A dictionary containing boolean values for mslevels.

    Returns:
    mslevel_str : str
        A string representing the selected mslevel.
    """
    if mslevel_bool_dict['ms1']:
        mslevel_str = 'ms1'
    elif mslevel_bool_dict['ms2']:
        mslevel_str = 'ms2'
    elif mslevel_bool_dict['ms1'] and mslevel_bool_dict['ms2']:
        mslevel_str = 'ms1ms2'
    else:
        raise ValueError('No mslevel selected')
    return mslevel_str

def check_ion_mobility(mzml_file, num_lines_to_check=10_000_000):
    """
    Check if the mzML file contains ion mobility data

    Args:
    mzml_file: (str) mzML file to load
    num_lines_to_check: (int) Number of lines to check for "Ion Mobility"

    Returns:
    Return a boolean indicating if the mzML file contains ion mobility data
    """
    has_ion_mobility = False
    with open(mzml_file, 'rb', 0) as file:
        s = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) 
        for line in iter(s.readline, b""):
            if b'Ion Mobility' in line:
                has_ion_mobility = True
                break 
            if s.tell() > num_lines_to_check:
                break
    return has_ion_mobility