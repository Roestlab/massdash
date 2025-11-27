# MassDash GitHub Copilot Development Instructions

This file provides comprehensive instructions for GitHub Copilot when working on the MassDash project. MassDash is a visualization and data exploration platform for Data-Independent Acquisition mass spectrometry data.

## ⚠️ CRITICAL NETWORK TIMEOUT WARNINGS

**NEVER CANCEL builds, installs, or tests that take longer than expected!**

- PyOpenMS installation can take 10-15 minutes due to large binary dependencies
- Core dependency installation typically takes 15-45 seconds but can timeout
- Documentation builds require pandoc and take ~21 seconds
- Full test suite runs ~450 tests in approximately 60 seconds
- Network timeouts are common - always use timeout values of 60+ minutes for builds

## Project Structure and Architecture

```
massdash/
├── massdash/                 # Main package directory
│   ├── dataProcessing/       # Data processing algorithms
│   ├── gui.py               # Streamlit GUI interface
│   ├── loaders/             # Data file loaders
│   ├── main.py              # CLI entry point
│   ├── peakPickers/         # Peak picking algorithms
│   ├── plotting/            # Visualization modules
│   ├── server/              # Web server components
│   ├── structs/             # Data structures and models
│   ├── testing/             # Testing utilities
│   └── ui/                  # UI components
├── test/                    # Test suite (~450 tests)
├── docs/                    # Documentation source
├── pyproject.toml           # Project configuration
└── requirements.txt         # Frozen dependencies
```

## Installation Instructions

### 1. Python Version Requirements
- **Supported versions**: Python 3.10, 3.11, 3.12
- **Current constraint**: `>=3.10, <3.13`
- If you encounter version conflicts, check `pyproject.toml` line 23

### 2. Core Dependencies Installation

**NEVER CANCEL - can take 10-15 minutes for PyOpenMS!**

```bash
# Basic installation with extended timeout (RECOMMENDED)
pip install --timeout 600 --retries 5 -e .

# Alternative: Install core dependencies separately if network issues persist
pip install --timeout 600 pyopenms>=3.2.0  # ~14 seconds typically, can timeout
pip install bokeh plotly matplotlib pandas numpy scipy  # ~15 seconds
pip install click joblib psutil tqdm upsetplot requests pyopenms_viz
```

### 3. Optional Dependencies

```bash
# GUI dependencies (for streamlit interface)
pip install massdash[gui]  # streamlit>=1.30.0, tk, pyautogui

# Documentation dependencies (~45 seconds)
pip install massdash[docs]  # sphinx, nbsphinx, sphinx-rtd-theme, etc.

# Testing dependencies
pip install massdash[testing]  # pytest, syrupy, tables

# All extras
pip install massdash[gui,docs,testing,conformer]
```

### 4. Network Timeout Handling

If you encounter network timeouts:

```bash
# Increase timeout and retry attempts
pip install --timeout 900 --retries 10 --index-url https://pypi.org/simple/ massdash

# Alternative: Use conda for PyOpenMS if pip fails
conda create -n massdash python=3.11
conda activate massdash
conda install -c conda-forge pyopenms
pip install -e .
```

## Build and Test Processes

### 1. Running Tests

**NEVER CANCEL - Full test suite takes ~60 seconds**

```bash
# Quick structure tests (~1 second)
python -m pytest test/structs -v

# Full test suite (~63 seconds, 450 tests)
python -m pytest -x --tb=short

# Specific test categories
python -m pytest test/loaders -v      # Data loader tests
python -m pytest test/plotting -v     # Visualization tests
python -m pytest test/peakPickers -v  # Algorithm tests

# Run with coverage
python -m pytest --cov=massdash --cov-report=html
```

### 2. Documentation Building

**Build time: ~21 seconds with pandoc**

```bash
cd docs/
make html  # Requires pandoc installation

# Alternative if pandoc missing
sudo apt-get install pandoc  # Linux
# or
brew install pandoc  # macOS
```

### 3. Code Quality and Linting

```bash
# Run any existing linters (check if configured)
python -m flake8 massdash/  # If configured
python -m black massdash/  # If configured
python -m isort massdash/  # If configured
```

## Development Workflows

### 1. Quick Development Validation
```bash
# Validate installation
python -c "import massdash; print('MassDash available')"
python -c "import pyopenms; print('PyOpenMS version:', pyopenms.__version__)"

# Run quick tests (~1 second)
python -m pytest test/structs -v

# Test CLI interface
python -m massdash --help
```

### 2. GUI Development
```bash
# Launch GUI (requires streamlit)
massdash gui
# or
python -m massdash gui
# or
streamlit run massdash/gui.py
```

### 3. Algorithm Development
```bash
# Test specific algorithm modules
python -c "from massdash.peakPickers import *"
python -c "from massdash.dataProcessing import *"
python -c "from massdash.plotting import *"
```

### 4. Data Structure Testing
```bash
# Quick validation of core structures
python -m pytest test/structs -v  # ~1 second
```

## Common Issues and Troubleshooting

### 1. PyOpenMS Installation Issues
- **Symptom**: TimeoutError during pip install
- **Solution**: Use conda or increase timeout to 900+ seconds
- **Alternative**: Install from pre-built wheels with `--only-binary=all`

### 2. Network Connectivity Issues
- **Symptom**: ReadTimeoutError from pypi.org
- **Solutions**:
  ```bash
  # Use alternative index
  pip install --index-url https://pypi.python.org/simple/ --trusted-host pypi.python.org massdash
  
  # Use conda-forge
  conda install -c conda-forge pyopenms bokeh plotly
  
  # Cache packages locally
  pip download massdash  # Download first, then install offline
  ```

### 3. Python Version Conflicts
- **Symptom**: "requires a different Python" error
- **Solution**: Check `pyproject.toml` line 23, ensure Python 3.10-3.12

### 4. GUI Dependencies Missing
- **Symptom**: ImportError for streamlit or tk
- **Solution**: `pip install massdash[gui]`

### 5. Test Failures
- **Common patterns**: Skip failing tests unrelated to your changes
- **Focus on**: Only fix tests related to your specific modifications
- **Validation**: Run `pytest test/structs -v` for quick sanity check

## Critical Validation Steps

Before submitting any changes:

1. **Validate core functionality**:
   ```bash
   python -c "import massdash; print('✓ Core import works')"
   python -m pytest test/structs -v  # Should complete in ~1 second
   ```

2. **Check for import issues**:
   ```bash
   python -c "from massdash.structs import *; print('✓ Structs import')"
   python -c "from massdash.plotting import *; print('✓ Plotting import')"
   ```

3. **Validate CLI**:
   ```bash
   python -m massdash --help  # Should show help without errors
   ```

4. **Run relevant tests only**:
   - Don't try to fix unrelated test failures
   - Focus on tests related to your changes
   - Use `-x` flag to stop on first failure for debugging

## Performance Expectations

- **PyOpenMS install**: 10-15 minutes (large binary, network dependent)
- **Core dependencies**: 15-45 seconds  
- **Structure tests**: ~1 second
- **Full test suite**: ~60 seconds (450 tests)
- **Documentation build**: ~21 seconds (with pandoc)
- **GUI startup**: 5-10 seconds (streamlit app)

## Alternative Installation Methods

### Docker Installation
```bash
# Pull pre-built container
docker pull singjust/massdash:latest
docker run -p 8501:8501 singjust/massdash:latest
```

### Conda Installation (Future)
```bash
# Note: Not yet available on conda-forge, but dependencies can be installed via conda
conda install -c conda-forge pyopenms bokeh plotly streamlit
pip install massdash
```

## File Patterns to Ignore

When using `.gitignore`, exclude these patterns:
```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.venv/
node_modules/  # If any JS components
.DS_Store
```

## Dependencies Summary

**Core (always required)**:
- pyopenms>=3.2.0 (mass spectrometry data handling)
- bokeh>3.0 (interactive plotting)
- plotly==5.24.1 (visualization)
- pandas>=0.17 (data manipulation)
- numpy>=1.9.0 (numerical computing)
- scipy>=1.12.0 (scientific computing)

**GUI (optional)**:
- streamlit>=1.30.0 (web app framework)
- tk (GUI toolkit)
- pyautogui (GUI automation)

**Documentation (optional)**:
- sphinx (documentation generator)
- nbsphinx (Jupyter notebook support)
- sphinx-rtd-theme (Read the Docs theme)

**Testing (optional)**:
- pytest (testing framework)
- syrupy (snapshot testing)
- tables (HDF5 support)

---

**Remember**: This is a mass spectrometry data analysis tool with heavy computational dependencies. Network timeouts and long installation times are normal. Be patient and use appropriate timeout values!