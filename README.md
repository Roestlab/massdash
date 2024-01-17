<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Light.png" alt="MassDash_Logo" width="500">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Logo_Dark.png" alt="MassDash_Logo" width="500">
    <img alt="MassDash Logo" comment="Placeholder to transition between light color mode and dark color mode - this image is not directly used." src="https://github.com/Roestlab/massdash/blob/dev/massdash/assets/img/MassDash_Logo_Dark.png">
  </picture>
</p>

---

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![pypiv](https://img.shields.io/pypi/v/massdash.svg)](https://pypi.python.org/pypi/massdash)
[![pypidownload](https://img.shields.io/pypi/dm/massdash?color=orange)](https://pypistats.org/packages/massdash)
[![dockerv](https://img.shields.io/docker/v/singjust/massdash?label=docker&color=green)](https://hub.docker.com/r/singjust/massdash)
[![dockerpull](https://img.shields.io/docker/pulls/singjust/massdash?color=green)](https://hub.docker.com/r/singjust/massdash)
[![readthedocs](https://img.shields.io/readthedocs/massdash)]([https://massdash.readthedocs.io/en/latest/Installation.html](https://massdash.readthedocs.io/en/latest/index.html))
[![Licence](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://raw.githubusercontent.com/RoestLab/massdash/main/LICENSE)

**MassDash** is a powerful platform designed for researchers and analysts in the field of mass spectrometry. By providing a centralized web-based dashboard, MassDash facilitates data analysis and experiment design by enabling users to visualize chromatograms, test algorithms, and optimize parameters. This tool offers a flexible environment for mass spectrometry research, with notable specailty in handling Data-Independent Acquisition (DIA) data.

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

Change into `massdash` directory:

```bash
cd massdash
```

Install `massdash` in editable mode:

```bash
pip install -e .
```

</details>

## Quick start

Launch MassDash by typing the following command in your terminal:

```bash
massdash gui
```

<p align="left">
  <img alt="MassDash Landing Page" style="width: 80%;" src="https://github.com/Roestlab/massdash/raw/dev/massdash/assets/img/MassDash_Landing_Page.png">
</p>

## Features

MassDash empowers researchers to streamline mass spectrometry workflows, experiment with data analysis algorithms, and optimize parameters to enhance research accuracy and efficiency. Below are some of MassDash's notable features:

- **Chromatogram visualization**: Easily view and analyze chromatograms for an in-depth examination of mass spectrometry data.

- **Algorithm testing**: Develop and fine-tune custom algorithms by interfacing with MassDash's various data analysis algorithms and workflows.

- **Parameter optimization**: Ensure optimal results for your experiment by optimizing parameters for data analysis workflows, such as *OpenSwathWorkflow*.

- **User-friendly dashboard**: MassDash's dashboard is designed with users in mind, facilitating research productivity in both beginners and experts in the field.

- **Data exploration**: Explore mass spectrometry data with our suite of tools and gain insights to make informed research decisions.

- **Customization**: Flexibly tailor data analysis parameters and results for specific research needs.

- **Rapid prototyping**: Save time and resource when developing mass spectrometry workflows by quickly prototyping and testing research ideas.

- **Data integration**: Seamlessly import, process, and export data to facilitate data sharing and collaboration.

## Launching MassDash from a remote machine

SSH into a remote machine and install `massdash`; it's highly recommended to install `massdash` in a Python virtual environment to contain project-specific dependencies:

```bash
ssh your_user_name@remote_ip_address
```

```bash
pip install massdash
```

Launch MassDash:

```bash
massdash gui
```

Two URLs with an IP address and port number will appear in the terminal after launching MassDash; for example:

```text
  Network URL: http://192.168.142.176:8501
  External URL: http://142.150.84.40:8501
```

 Enter the following command in a local machine's terminal, replacing "----" with the URL port number (e.g., 8501):

```bash
ssh -fNL ----:localhost:---- your_user_name@remote_ip_address
```

You can now view MassDash on the local machine's browser by clicking on either of the provided URLs.

## Docker

MassDash is also available on Docker.

Pull the latest stable version of MassDash from DockerHub:

```bash
docker pull singjust/massdash:latest
```

Spin up the MassDash Docker container:

```bash
docker run -p 8501:8501 singjust/massdash:latest
```

**Note:** The MassDash Docker image binds to port 8501 when running MassDash locally.

## Contribute

* [Issues Tracker](https://github.com/Roestlab/massdash/issues)
* [Source Code](https://github.com/Roestlab/massdash/tree/main/massdash)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/Roestlab/massdash/issues).

## License

This project is licensed under the BSD 3-Clause license.
