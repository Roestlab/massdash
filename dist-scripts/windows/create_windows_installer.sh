#!/bin/sh

# This script is used to create the Linux installer for the application.

echo "[$(date)] INFO - Cleaning up the previous build and dist folders"
rm -rf dist
rm -rf build
cd ../../
rm -rf dist
rm -rf build

# Create a fresh conda environment
echo "[$(date)] INFO - Creating a fresh conda environment"
conda create -n massdash_pyinstaller python=3.9 -y
conda activate massdash_pyinstaller

# Install the required packages
echo "[$(date)] INFO - Installing required packages"
pip install -r requirements.txt
pip install onnxruntime
pip install torch
pip install torchmetrics
pip install setuptools
pip install build
pip install pyinstaller
echo "[$(date)] INFO - Building and installing massdash"
python -m build
pip install dist/massdash-0.0.8-py3-none-any.whl

cd dist-scripts/windows

# Create the installer
echo "[$(date)] INFO - Creating the installer"
pyinstaller ../pyinstaller/massdash.spec -y
conda deactivate

# Create an .exe package
echo "[$(date)] INFO - Creating an .exe package"
