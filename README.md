<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Light.png" alt="MassDash_Logo" width="500">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Dark.png" alt="MassDash_Logo" width="500">
    <img alt="MassDash Logo" comment="Placeholder to transition between light color mode and dark color mode - this image is not directly used." src="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Dark.png">
  </picture>
</p>

---

[![pypipv](https://img.shields.io/pypi/pyversions/massdash.svg)](https://img.shields.io/pypi/pyversions/massdash)
[![pypiv](https://img.shields.io/pypi/v/massdash.svg)](https://pypi.python.org/pypi/massdash)
[![pypidownload](https://img.shields.io/pypi/dm/massdash?color=orange)](https://pypistats.org/packages/massdash)
<!-- 
[![biocondav](https://img.shields.io/conda/v/bioconda/massdash?label=bioconda&color=purple)](https://anaconda.org/bioconda/massdash)
-->
[![dockerv](https://img.shields.io/docker/v/singjust/massdash?label=docker&color=green)](https://hub.docker.com/r/singjust/massdash)
[![dockerpull](https://img.shields.io/docker/pulls/singjust/massdash?color=green)](https://hub.docker.com/r/singjust/massdash)
[![continuous-integration](https://github.com/Roestlab/massdash/workflows/continuous-integration/badge.svg)](https://github.com/Roestlab/massdash/actions)
[![demoapp](https://img.shields.io/badge/demo-massdash.streamlit.app-brightgreen?link=https%3A%2F%2Fmassdash.streamlit.app%2F)](https://massdash.streamlit.app/)
[![readthedocs](https://img.shields.io/readthedocs/massdash)](https://massdash.readthedocs.io/en/latest/index.html)
[![Licence](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://raw.githubusercontent.com/RoestLab/massdash/main/LICENSE)

**MassDash** is a visualization and data exploration platform for Data-Independent Acquisition mass spectrometry data. 

Key Features Include:
- **Chromatogram Visualization** - Easily view and analyze chromatograms for an in-depth examination of peptide precursors of interest.
- **2D and 3D Visualizations** - Visualization of ion mobility enhacanced mass spectrometry and other 2D and 3D plots.
- **On the fly parameter optimization** - Adjust peak picking parameters on the fly or experiment with novel deep learning based peak picking approaches. 
- **Algorithm testing** -  Develop and fine-tune custom algorithms by interfacing with MassDash's various data analysis algorithms and workflows.
- **Usage Flexibility** - User-friendly web based dashboard for quick visualizations, advanced python package for more complex applications 

## One Click Installation

[![installwindows](https://img.shields.io/badge/install-windows-blue?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_windows.exe)](https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_windows.exe)
[![installmacos](https://img.shields.io/badge/install-macos-white?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_macos.pkg)](https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_macos.pkg)
[![installubuntu](https://img.shields.io/badge/install-ubuntu-purple?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_linux.deb)](https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_linux.deb)
[![demoapp](https://img.shields.io/badge/demo-massdash.streamlit.app-brightgreen?link=https%3A%2F%2Fmassdash.streamlit.app%2F)](https://massdash.streamlit.app/)

For a one-click installation, click on the corresponding badge corresponding to your operating system, or visit the [latest release page](https://github.com/Roestlab/massdash/releases/latest) and download the installer for your operating system.

## (Recommended) Pip Installation

The recommended way of installing MassDash is through the Python Package Index (PyPI). We recommend installing MassDash in its own virtual environment using Anaconda to avoid packaging conflicts.

First create a new environemnt:

```bash
conda create --name=massdash python=3.9
conda activate massdash 
```
Then in the new environment install MassDash.

```bash
pip install massdash --upgrade
```

After installation the GUI can be launched in the Terminal/Anaconda Prompt using 

```bash
massdash gui
```


<!-- 
or, install the latest stable version of MassDash from Bioconda if you are using Anaconda for package and environment management:

```bash
conda install bioconda::massdash --upgrade
```
-->

For detailed OS-specific (Windows, MacOS, Ubuntu) installation guides, please refer to the [documentation](https://massdash.readthedocs.io/en/latest/Installation.html#installation-guides).

## GUI Quick start

Launch MassDash by typing the following command in your terminal/Anaconda Prompt:

```bash
massdash gui
```

For more information on the GUI, please refer to the [documentation](https://massdash.readthedocs.io/en/latest/GUI.html).

<p align="left">
  <img alt="MassDash Landing Page" style="width: 80%;" src="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Landing_Page.png">
</p>

## Demo

To run a demo version of MassDash, you can visit the streamlit cloud hosted demo version [here](https://massdash.streamlit.app/). Note that full functionality is not avaliable in the demo app.


## Documentation

For more information (API and tutorial walk-throughs), please refer to the [documentation](https://massdash.readthedocs.io/en/latest/index.html).

## Contribute

* [Issues Tracker](https://github.com/Roestlab/massdash/issues)
* [Source Code](https://github.com/Roestlab/massdash/tree/main/massdash)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/Roestlab/massdash/issues).

## License

This project is licensed under the BSD 3-Clause license.

## Citation

MassDash: A Web-Based Dashboard for Data-Independent Acquisition Mass Spectrometry Visualization
Justin C. Sing, Joshua Charkow, Mohammed AlHigaylan, Ira Horecka, Leon Xu, and Hannes L. Röst
Journal of Proteome Research 2024 23 (6), 2306-2314
DOI: 10.1021/acs.jproteome.4c00026
