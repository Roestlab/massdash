# -*- mode: python ; coding: utf-8 -*-

import site
import importlib.metadata
import os
import sys

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

from transformers.dependency_versions_check import pkgs_to_check_at_runtime

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

##################### User definitions
exe_name = 'massdash_gui'
script_name = 'run.py'
if sys.platform[:6] == "darwin":
	icon = '../../massdash/assets/img/MassDash_Logo.icns'
else:
	icon = '../../massdash/assets/img/MassDash_Logo.ico'
block_cipher = None
location = os.getcwd()
project = "massdash"
remove_tests = True
bundle_name = "massdash"
#####################


requirements = {project, "streamlit_javascript", "upsetplot", "distributed"}
datas = [(f"{site.getsitepackages()[0]}/streamlit/runtime", "./streamlit/runtime")]
hidden_imports = set()
binaries = []
checked = set()
while requirements:
	requirement = requirements.pop()
	print(f"Info: Checking {requirement}")
	checked.add(requirement)
	if requirement in ["pywin32"]:
		continue
	try:
		module_version = importlib.metadata.version(requirement)
	except (
		importlib.metadata.PackageNotFoundError,
		ModuleNotFoundError,
		ImportError
	):
		continue
	try:
		datas_, binaries_, hidden_imports_ = collect_all(
			requirement,
			include_py_files=True
		)
	except ImportError:
		continue
	datas += datas_
	# binaries += binaries_
	hidden_imports_ = set(hidden_imports_)
	if "" in hidden_imports_:
		hidden_imports_.remove("")
	if None in hidden_imports_:
		hidden_imports_.remove(None)
	requirements |= hidden_imports_ - checked
	hidden_imports |= hidden_imports_

if remove_tests:
	hidden_imports = sorted(
		[h for h in hidden_imports if "test" not in h.split(".")]
	)
else:
	hidden_imports = sorted(hidden_imports)


hidden_imports = [h for h in hidden_imports if "__pycache__" not in h]
datas = [d for d in datas if ("__pycache__" not in d[0]) and (d[1] not in [".", "Resources", "scripts"])]

#if sys.platform[:5] == "win32":
#	base_path = os.path.dirname(sys.executable)
#	library_path = os.path.join(base_path, "Library", "bin")
#	dll_path = os.path.join(base_path, "DLLs")
#	libcrypto_dll_path = os.path.join(dll_path, "libcrypto-1_1-x64.dll")
#	libssl_dll_path = os.path.join(dll_path, "libssl-1_1-x64.dll")
#	libcrypto_lib_path = os.path.join(library_path, "libcrypto-1_1-x64.dll")
#	libssl_lib_path = os.path.join(library_path, "libssl-1_1-x64.dll")
#	if not os.path.exists(libcrypto_dll_path):
#		datas.append((libcrypto_lib_path, "."))
#	if not os.path.exists(libssl_dll_path):
#		datas.append((libssl_lib_path, "."))

for _pkg in ["python","accelerate"]:
	if _pkg in pkgs_to_check_at_runtime:
		pkgs_to_check_at_runtime.remove(_pkg)
for _pkg in pkgs_to_check_at_runtime:
	datas += copy_metadata(_pkg)


datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")
datas += collect_data_files("pyopenms")
datas += copy_metadata("pyopenms")
datas += collect_data_files("massdash")
datas += copy_metadata("massdash")

hidden_imports = ['pyopenms', 'massdash', 'torchaudio.lib.libtorchaudio']

a = Analysis(
	[script_name],
	pathex=[location],
	binaries=binaries,
	datas=datas,
	hiddenimports=hidden_imports,
	hookspath=['./hooks'],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False
)
pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
)

if sys.platform[:5] == "linux":
	exe = EXE(
		pyz,
		a.scripts,
		a.binaries,
		a.zipfiles,
		a.datas,
		name=bundle_name,
		debug=False,
		bootloader_ignore_signals=False,
		strip=False,
		upx=True,
		console=True,
		upx_exclude=[],
		icon=icon
	)
else:
	exe = EXE(
		pyz,
		a.scripts,
		# a.binaries,
		a.zipfiles,
		# a.datas,
		exclude_binaries=True,
		name=exe_name,
		debug=False,
		bootloader_ignore_signals=False,
		strip=False,
		upx=True,
		console=True,
		icon=icon
	)
	coll = COLLECT(
		exe,
		a.binaries,
		# a.zipfiles,
		a.datas,
		strip=False,
		upx=True,
		upx_exclude=[],
		name=exe_name
	)