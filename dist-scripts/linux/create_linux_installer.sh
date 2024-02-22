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

cd dist-scripts/linux

# Create the installer
echo "[$(date)] INFO - Creating the installer"
pyinstaller ../pyinstaller/massdash.spec -y

# Create the debian package
echo "[$(date)] INFO - Creating the debian package"
mkdir -p dist/massdash_linux/usr/local/bin
mv dist/massdash dist/massdash_linux/usr/local/bin/massdash
mkdir dist/massdash_linux/DEBIAN
mkdir -p dist/massdash_linux/usr/share/applications
mkdir -p dist/massdash_linux/usr/share/icons
cp massdash.desktop dist/massdash_linux/usr/share/applications/massdash.desktop
cp ../../massdash/assets/img/MassDash_Logo.ico dist/massdash_linux/usr/share/icons/massdash.ico
cp control dist/massdash_linux/DEBIAN/control
dpkg-deb --build --root-owner-group dist/massdash_linux