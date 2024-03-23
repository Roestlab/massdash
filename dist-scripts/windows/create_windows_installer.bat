@echo off
rem This script is used to create the Windows installer for the application.

rem Clean up the previous build and dist folders
echo INFO - Cleaning up the previous build and dist folders
rmdir /s /q dist
rmdir /s /q build
cd ..
rmdir /s /q dist
rmdir /s /q build
cd dist-scripts\windows

rem Create a fresh conda environment
echo INFO - Creating a fresh conda environment
@REM call conda create -n massdash_pyinstaller python=3.9 -y
call conda activate massdash_pyinstaller

rem Install the required packages
echo INFO - Installing required packages
conda install pip -y
pip install -r requirements.txt
@REM pip install numpy==1.24.2
pip install tk
pip install onnxruntime
@REM pip install torch
@REM pip install torchmetrics
@REM pip install transformers
pip install setuptools
pip install build
pip install pyinstaller==6.4.0
echo INFO - Building and installing massdash
python -m build
pip install dist\massdash-0.0.8-py3-none-any.whl

rem Create the installer
echo INFO - Creating the installer
pyinstaller ../pyinstaller/massdash.spec -y
call conda deactivate

@REM rem Create an .exe package
@REM echo INFO - Creating an .exe package
@REM "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" massdash_innoinstaller.iss
