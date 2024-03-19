#!/bin/bash

# This script is used to create the Windows installer for the application.

# Initialize conda (replace 'bash' with your shell if needed)
conda init bash

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
conda install pip -y
pip install -r requirements.txt
pip install --upgrade --force-reinstall numpy
pip install onnxruntime
pip install torch
pip install torchmetrics
pip install transformers
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
# echo "[$(date)] INFO - Creating an .exe package"
# "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" massdash_innoinstaller.iss