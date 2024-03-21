#!/bin/sh

# # This script is used to create the macOS installer for the application.

# echo "[$(date)] INFO - Cleaning up the previous build and dist folders"
# rm -rf dist
# rm -rf build
# cd ../../
# rm -rf dist
# rm -rf build

# # Create a fresh conda environment
# echo "[$(date)] INFO - Creating a fresh conda environment"
# conda create -n massdash_pyinstaller python=3.9 -y
# conda activate massdash_pyinstaller

# # Install the required packages
# echo "[$(date)] INFO - Installing required packages"
pip install nomkl
pip install -r requirements.txt
pip install tk
pip install onnxruntime
pip install torch
pip install torchmetrics
pip install transformers
pip install setuptools
pip install build
pip install pyinstaller==6.4.0
# echo "[$(date)] INFO - Building and installing massdash"
# python -m build
# pip install dist/massdash-0.0.8-py3-none-any.whl

# cd dist-scripts/macos

# # Create the installer
# echo "[$(date)] INFO - Creating the installer"
# pyinstaller ../pyinstaller/massdash.spec -y
# conda deactivate

# Create the macos package
mkdir -p dist/massdash/Contents/Resources
cp ../../massdash/assets/img/MassDash_Logo.icns dist/massdash/Contents/Resources
mkdir dist/massdash/Contents/MacOS
mv dist/massdash/massdash dist/massdash/Contents/MacOS
mkdir dist/massdash/Contents/Frameworks
cp -r dist/massdash/_internal/* dist/massdash/Contents/Frameworks/
cp Info.plist dist/massdash/Contents
cp massdash_terminal dist/massdash/Contents/MacOS
cp ../../LICENSE Resources/LICENSE
cp ../../massdash/assets/img/MassDash_Logo_Dark.png Resources/MassDash_Logo_Dark.png 
chmod 777 scripts/*

pkgbuild --root dist/massdash --identifier uoft.molgen.massdash.app --version 0.0.8 --install-location /Applications/massdash.app --scripts scripts massdash.pkg
productbuild --distribution distribution.xml --resources Resources --package-path massdash.pkg dist/massdash_macos.pkg