<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Light.png" alt="MassDash_Logo" width="500">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Dark.png" alt="MassDash_Logo" width="500">
    <img comment="Placeholder to transition between light color mode and dark color mode - this image is not directly used." src="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Logo_Dark.png">
  </picture>
</p>
MassDash_Landing_Page.png

[![pypiv](https://img.shields.io/pypi/v/massdash.svg)](https://pypi.python.org/pypi/massdash)
[![pypidownload](https://img.shields.io/pypi/dm/massdash?color=orange)](https://pypistats.org/packages/massdash)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![dockerv](https://img.shields.io/docker/v/singjust/massdash?label=docker&color=green)](https://hub.docker.com/r/singjust/massdash)
[![dockerpull](https://img.shields.io/docker/pulls/singjust/massdash?color=green)](https://hub.docker.com/r/singjust/massdash)
[![Licence](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://raw.githubusercontent.com/RoestLab/massdash/main/LICENSE)

MassDash is a powerful platform designed for researchers and analysts in the field of mass spectrometry. By providing a centralized web-based dashboard, MassDash facilitates data analysis and experiment design by enabling users to visualize chromatograms, test algorithms, and optimize parameters. This tool offers a flexible environment for mass spectrometry research, with notable specailty in handling Data-Independent Acquisition (DIA) data.

## Installation

**Recommended**: Install the latest stable version of MassDash from the Python Package Index (PyPI):

```bash
pip install massdash --upgrade
```

<details>
   <summary>Installing from source</summary>

Clone the repository:

```bash
git clone https://github.com/Roestlab/massdash.git
```

Change into massdash directory:

```bash
cd massdash
```

Install massdash in editable mode:

```bash
pip install -e .
```

</details>

## Quick start

To open up MassDash in your browser, simply type the following in your terminal:

```bash
massdash gui
```

<p align="center">
  <img alt="MassDash Landing Page" src="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Landing_Page.png">
</p>

## Features

MassDash empowers researchers to streamline mass spectrometry workflows, experiment with data analysis algorithms, and optimize parameters to enhance research accuracy and efficiency. Below are some of MassDash's notable features:

**Chromatogram visualization**: Easily view and analyze chromatograms for an in-depth examination of mass spectrometry data.

**Algorithm testing**: Develope and fine-tune custom algorithms by interfacing with MassDash's various data analysis algorithms and workflows.

**Parameter optimization**: Ensure optimal results for your experiment by optimizing parameters for data analysis workflows, such as *OpenSwathWorkflow*.

**User-friendly dashboard**: MassDash's dashboard is designed with users in mind, facilitating research productivity in both beginners and experts in the field.

**Data Exploration**: Explore your mass spectrometry data with our suite of tools and gain insights to make informed research decisions.

**Customization**: Flexibly tailor your data analysis parameters and results for your specific research needs.

**Rapid Prototyping**: Save time and resource when developing mass spectrometry workflows by quickly prototyping and testing research ideas.

**Data Integration**: Seamlessly import, process, and export data to facilitate data sharing and collaboration.

## Launching MassDash GUI from a remote machine

SSH into your remote machine and install `massdash`; installing `massdash` inside a Python virtual environment is highly recommended to contain project-specific dependencies:

```bash
your_user_name@remote_ip_address
```

```bash
pip install massdash
```

Launch the MassDash GUI:

```bash
massdash gui
```

In your terminal, you will receive a message providing two URLs with and IP address and port; for example:

```text
  Network URL: http://192.168.142.176:8501
  External URL: http://142.150.84.40:8501
```

Open a terminal window in your local machine and enter the following command, replacing "----" with the URL port number (e.g., 8501):

```bash
ssh -fNL ----:localhost:---- your_user_name@remote_ip_address
```

You can now view the MassDash GUI on your local machine's browser by clicking on either of the provided URLs.

## Docker

MassDash is also available from Docker.

Pull the latest stable version of MassDash from DockerHub:

```bash
docker pull singjust/massdash:latest
```

Spin up the Docker container:

```bash
docker run -p 8501:8501 singjust/massdash:latest
```

**Note:** The Docker image binds to port 8501 when running MassDash locally.

## Contribute

* [Issues Tracker](https://github.com/Roestlab/massdash/issues)
* [Source Code](https://github.com/Roestlab/massdash/tree/main/massdash)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/Roestlab/massdash/issues).

## License

This project is licensed under the BSD 3-Clause license.
