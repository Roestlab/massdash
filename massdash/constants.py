"""
massdash/constants
~~~~~~~~~~~~~~~~~~
"""

import os
import platform
from PIL import Image

USER_PLATFORM_SYSTEM = platform.system()

MASSDASH_DIRNAME = os.path.dirname(__file__)

######################
## Icons
MASSDASH_ICON = Image.open(os.path.normpath(os.path.join(MASSDASH_DIRNAME, 'assets/img/MassDash_Logo.ico')))
MASSDASH_LOGO_LIGHT = Image.open(os.path.normpath(os.path.join(MASSDASH_DIRNAME, 'assets/img/MassDash_Logo_Light.png')))
MASSDASH_LOGO_DARK = Image.open(os.path.normpath(os.path.join(MASSDASH_DIRNAME, 'assets/img/MassDash_Logo_Dark.png')))
OPENMS_LOGO = Image.open(os.path.normpath(os.path.join(MASSDASH_DIRNAME, 'assets/img/OpenMS.png')))

######################
## URLS

# Test Data
URL_TEST_SQMASS = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/openswath/xics/test_raw_1.sqMass"
URL_TEST_OSW = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/openswath/osw/test.osw"
URL_TEST_PQP = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/openswath/lib/test.pqp"
URL_TEST_RAW_MZML = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/raw/test_raw_1.mzML"
URL_TEST_DREAMDIA_REPORT = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/dreamdia/test_dreamdia_report.tsv"
URL_PRETRAINED_CONFORMER = "https://github.com/Roestlab/massdash/releases/download/v0.0.1-alpha/base_cape.onnx"
URL_TEST_RAW_MZML_IM = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/mzml/ionMobilityTest.mzML"
URL_TEST_OSW_IM = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/osw/ionMobilityTest.osw"

######################
## Data Handling

# Data Smoothing
SMOOTHING_DICT = {'No Smoothing': {'type': 'none'},
                  'Savitzky-Golay': {'type': 'sgolay', 'sgolay_polynomial_order': 3, 'sgolay_frame_length': 11},
                  'Gaussian': {'type': 'gauss', 'gaussian_sigma': 2.0, 'gaussian_window': 11}
                 }
