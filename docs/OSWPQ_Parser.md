# OSWPQ File Parser Documentation

## Overview

The OSWPQResultsAccess class provides support for parsing .oswpq files in MassDash. An .oswpq file is a directory containing two Parquet files with OpenSWATH results data:

- `precursors_features.parquet` - Contains precursor-level features and scoring information
- `transition_features.parquet` - Contains transition-level features and intensities

## Usage

### Basic Usage

```python
from massdash.loaders.ResultsLoader import ResultsLoader

# Load OSWPQ results
results_loader = ResultsLoader('/path/to/results.oswpq')

# Or load multiple result files including OSWPQ
results_loader = ResultsLoader([
    '/path/to/results.oswpq',
    '/path/to/other_results.osw',
    '/path/to/report.tsv'
])
```

### Direct Access

```python
from massdash.loaders.access.OSWPQResultsAccess import OSWPQResultsAccess

# Direct access to OSWPQ data
access = OSWPQResultsAccess('/path/to/results.oswpq')

# Get identified precursors
precursors = access.getIdentifiedPrecursors(qvalue=0.01)

# Get run names
runs = access.getRunNames()

# Check if data contains ion mobility
has_im = access.has_im
```

## File Structure Requirements

The .oswpq directory must contain exactly these two files:

```
results.oswpq/
├── precursors_features.parquet
└── transition_features.parquet
```

## Supported Schema

The parser supports the full OpenSWATH-OSWPQ schema as specified in the issue:

### Precursors Features Schema
- Protein information: `PROTEIN_ID`, `PROTEIN_ACCESSION`, `GENE_NAME`
- Peptide information: `PEPTIDE_ID`, `UNMODIFIED_SEQUENCE`, `MODIFIED_SEQUENCE`
- Precursor information: `PRECURSOR_ID`, `PRECURSOR_MZ`, `PRECURSOR_CHARGE`
- Feature information: `EXP_RT`, `EXP_IM`, `LEFT_WIDTH`, `RIGHT_WIDTH`
- Intensity measurements: `FEATURE_MS1_AREA_INTENSITY`, `FEATURE_MS2_AREA_INTENSITY`
- Scoring: `SCORE_MS2_Q_VALUE`, `SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE`
- Run information: `RUN_ID`, `FILENAME`

### Transitions Features Schema
- Identifiers: `TRANSITION_ID`, `PRECURSOR_ID`, `RUN_ID`
- Transition properties: `PRODUCT_MZ`, `TRANSITION_CHARGE`, `TRANSITION_TYPE`
- Intensities: `FEATURE_TRANSITION_AREA_INTENSITY`, `FEATURE_TRANSITION_APEX_INTENSITY`

## Features

### Q-value Filtering
The parser supports filtering at multiple levels:

```python
# Precursor-level filtering (default)
precursors = access.getIdentifiedPrecursors(qvalue=0.01, precursorLevel=True)

# Peptide/protein-level filtering
precursors = access.getIdentifiedPrecursors(qvalue=0.01, precursorLevel=False)
```

### Ion Mobility Support
Automatic detection and handling of ion mobility data:

```python
if access.has_im:
    print("Data contains ion mobility information")
    features = access.getTransitionGroupFeaturesDf('run1', 'PEPTIDE', 2)
    print(features['consensusApexIM'])  # IM values included
```

### Run-specific Queries
Support for querying specific runs or all runs:

```python
# Get precursors for specific run
precursors_run1 = access.getIdentifiedPrecursors(run='run1')

# Get precursors for all runs (returns dict)
all_precursors = access.getIdentifiedPrecursors()
```

## Integration with MassDash

The OSWPQResultsAccess integrates seamlessly with the existing MassDash infrastructure:

1. **Automatic Recognition**: ResultsLoader automatically detects .oswpq directories
2. **Unified Interface**: Same methods as other results access classes
3. **Consistent Output**: Returns the same data structures as OSW and TSV parsers

## Error Handling

The parser includes comprehensive error handling:

- Validates directory structure
- Checks for required Parquet files
- Handles missing columns gracefully
- Provides informative error messages

```python
try:
    access = OSWPQResultsAccess('/path/to/invalid.oswpq')
except FileNotFoundError as e:
    print(f"Required file missing: {e}")
except ValueError as e:
    print(f"Invalid directory structure: {e}")
```

## Performance Considerations

- Parquet files are loaded once during initialization
- Large datasets are handled efficiently through pandas/PyArrow
- Memory usage scales with the size of the feature tables
- Filtering operations are performed in-memory for fast access

## Dependencies

- pandas >= 2.0
- pyarrow >= 19.0
- Python >= 3.10

## Software Identification

The parser identifies itself as "OpenSWATH-OSWPQ" in the software field, distinguishing it from regular OpenSWATH (.osw) results.