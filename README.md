<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Logo_Light.png" alt="MassDash_Logo" width="500">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Logo_Dark.png" alt="MassDash_Logo" width="500">
    <img comment="Placeholder to transition between light color mode and dark color mode - this image is not directly used." src="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Logo_Dark.png">
  </picture>
</p>

[![pypiv](https://img.shields.io/pypi/v/massdash.svg)](https://pypi.python.org/pypi/massdash)
[![pypidownload](https://img.shields.io/pypi/dm/massdash?color=orange)](https://pypistats.org/packages/massdash)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://raw.githubusercontent.com/RoestLab/massdash/main/LICENSE)

MassDash is a powerful platform designed for researchers and analysts in the field of mass spectrometry. It enables the visualization of chromatograms (spectra and ion mobiliograms to come...) and provides a flexible environment for rapid algorithm testing and parameter optimization, crucial for data analysis and experimental design. This tool is an indispensable asset for researchers and laboratories working with DIA (Data-Independent Acquisition) data.

Key Features:

- **Chromatogram Visualization**: View and analyze chromatograms with ease, allowing for in-depth examination of mass spectrometry data.

- **Algorithm Testing**: Experiment with various data analysis algorithms and workflows, facilitating the development and fine-tuning of custom algorithms.

- **Parameter Optimization**: Optimize parameters for data analysis tools like OpenSwathWorkflow, ensuring the best results for your specific experiments.

- **User-Friendly Interface**: A user-friendly and intuitive interface makes it accessible to both beginners and experts in the field.

- **Data Exploration**: Dive into your mass spectrometry data, investigate peaks, and gain insights to make informed decisions.

- **Customization**: Adapt the tool to your specific research needs, allowing for tailored analysis and results.

- **Rapid Prototyping**: Quickly prototype and test ideas, saving time and resources in the development of mass spectrometry workflows.

- **Data Integration**: Seamlessly import, process, and export data, facilitating data sharing and collaboration.

This tool empowers researchers to take control of their mass spectrometry data, experiment with algorithms, and optimize parameters to enhance the accuracy and efficiency of their research. It's a valuable resource for laboratories and researchers working in the field of mass spectrometry, streamlining their workflows and contributing to scientific advancements.

# Installation

Install the stable version of MassDash from the Python Package Index (PyPI):

```
pip install massdash
```

<details>
   <summary>Installing from source</summary>

Clone the repository

```
git clone https://github.com/Roestlab/massdash.git
```

Change into massdash directory

```
cd massdash
```

Pip install massdash in editable mode

```
pip install -e .
```

</details>


# Running MassDash GUI

```
massdash gui
```

# Running MassDash GUI from a Remote Machine

Login to your remote machine

```
your_user_name@remote_ip_address
```

Navigate to massdash directory and start GUI. 

```
massdash gui
```

You will receive a message letting you know you can view Streamlit app in your browser with two URLs. 

```
  Network URL: http://192.168.142.176:8501
  External URL: http://142.150.84.40:8501
```

In your local machine, start a fresh terminal window. And enter the following command. Replace '----' with the last 4 digits from the URLs above. In this example, '----' would be 8501.

```
ssh -NfL localhost:----:localhost:---- your_user_name@remote_ip_address
```

Now you can copy Network/External url to your local machine browser and use massdash. 
