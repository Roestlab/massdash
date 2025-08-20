"""
test/loaders/access/test_OSWPQResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import tempfile
import pytest
import pandas as pd
from pathlib import Path

from massdash.loaders.access.OSWPQResultsAccess import OSWPQResultsAccess

class TestOSWPQResultsAccess:
    """Test class for OSWPQResultsAccess"""

    @pytest.fixture
    def mock_oswpq_data(self):
        """Create mock OSWPQ data for testing"""
        # Create sample precursors data
        precursors_data = {
            'PROTEIN_ID': [1, 2],
            'PEPTIDE_ID': [1, 2], 
            'IPF_PEPTIDE_ID': [1, 2],
            'PRECURSOR_ID': [1, 2],
            'PROTEIN_ACCESSION': ['P12345', 'P67890'],
            'UNMODIFIED_SEQUENCE': ['PEPTIDE', 'SEQUENCE'],
            'MODIFIED_SEQUENCE': ['PEPTIDE', 'SEQUENCE'],
            'PRECURSOR_TRAML_ID': ['tr_1', 'tr_2'],
            'PRECURSOR_GROUP_LABEL': ['group_1', 'group_2'],
            'PRECURSOR_MZ': [500.25, 600.30],
            'PRECURSOR_CHARGE': [2, 3],
            'PRECURSOR_LIBRARY_INTENSITY': [1000.0, 1500.0],
            'PRECURSOR_LIBRARY_RT': [100.0, 200.0],
            'PRECURSOR_LIBRARY_DRIFT_TIME': [10.0, 15.0],
            'GENE_ID': [1, 2],
            'GENE_NAME': ['GENE1', 'GENE2'],
            'GENE_DECOY': [0, 0],
            'PROTEIN_DECOY': [0, 0],
            'PEPTIDE_DECOY': [0, 0],
            'PRECURSOR_DECOY': [0, 0],
            'RUN_ID': [1, 1],
            'FILENAME': ['run1.mzML', 'run1.mzML'],
            'FEATURE_ID': [1, 2],
            'EXP_RT': [100.5, 200.5],
            'EXP_IM': [10.5, 15.5],
            'NORM_RT': [0.5, 0.6],
            'DELTA_RT': [0.1, 0.2],
            'LEFT_WIDTH': [95.0, 195.0],
            'RIGHT_WIDTH': [105.0, 205.0],
            'FEATURE_MS1_AREA_INTENSITY': [5000.0, 6000.0],
            'FEATURE_MS1_APEX_INTENSITY': [1000.0, 1200.0],
            'FEATURE_MS1_EXP_IM': [10.5, 15.5],
            'FEATURE_MS1_DELTA_IM': [0.1, 0.2],
            'FEATURE_MS2_AREA_INTENSITY': [4000.0, 5000.0],
            'FEATURE_MS2_APEX_INTENSITY': [800.0, 1000.0],
            'FEATURE_MS2_EXP_IM': [10.5, 15.5],
            'SCORE_MS2_Q_VALUE': [0.001, 0.005],
            'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE': [0.001, 0.005]
        }
        
        # Create sample transitions data (minimal)
        transitions_data = {
            'RUN_ID': [1, 1],
            'IPF_PEPTIDE_ID': [1, 2],
            'PRECURSOR_ID': [1, 2],
            'TRANSITION_ID': [1, 2],
            'TRANSITION_TRAML_ID': ['tr_1_1', 'tr_2_1'],
            'PRODUCT_MZ': [300.15, 400.20],
            'TRANSITION_CHARGE': [1, 1],
            'TRANSITION_TYPE': ['y', 'b'],
            'TRANSITION_ORDINAL': [1, 1],
            'ANNOTATION': ['y3', 'b2'],
            'TRANSITION_DETECTING': [1, 1],
            'TRANSITION_LIBRARY_INTENSITY': [500.0, 600.0],
            'TRANSITION_DECOY': [0, 0],
            'FEATURE_ID': [1, 2],
            'FEATURE_TRANSITION_AREA_INTENSITY': [2000.0, 2500.0]
        }
        
        return pd.DataFrame(precursors_data), pd.DataFrame(transitions_data)

    @pytest.fixture
    def mock_oswpq_dir(self, mock_oswpq_data):
        """Create a temporary directory with mock OSWPQ files"""
        precursors_df, transitions_df = mock_oswpq_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save the mock data as parquet files
            precursors_file = os.path.join(tmpdir, 'precursors_features.parquet')
            transitions_file = os.path.join(tmpdir, 'transition_features.parquet')
            
            precursors_df.to_parquet(precursors_file)
            transitions_df.to_parquet(transitions_file)
            
            yield tmpdir

    def test_init_valid_directory(self, mock_oswpq_dir):
        """Test initialization with valid OSWPQ directory"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        assert access.precursors_df is not None
        assert access.transitions_df is not None
        assert len(access.precursors_df) == 2
        assert len(access.transitions_df) == 2

    def test_init_invalid_directory(self):
        """Test initialization with invalid directory"""
        with pytest.raises(ValueError):
            OSWPQResultsAccess("/non/existent/path")

    def test_init_missing_files(self):
        """Test initialization with directory missing required files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                OSWPQResultsAccess(tmpdir)

    def test_has_im_property(self, mock_oswpq_dir):
        """Test has_im property"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        assert access.has_im == True  # Our mock data has IM columns

    def test_get_run_names(self, mock_oswpq_dir):
        """Test getRunNames method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        run_names = access.getRunNames()
        assert len(run_names) == 1
        assert 'run1' in run_names

    def test_get_software(self, mock_oswpq_dir):
        """Test getSoftware method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        assert access.getSoftware() == "OpenSWATH-OSWPQ"

    def test_get_identified_precursors(self, mock_oswpq_dir):
        """Test getIdentifiedPrecursors method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        # Test for all runs
        precursors = access.getIdentifiedPrecursors(qvalue=0.01)
        assert isinstance(precursors, dict)
        
        # Test for specific run
        precursors_run = access.getIdentifiedPrecursors(qvalue=0.01, run='run1')
        assert isinstance(precursors_run, set)
        assert len(precursors_run) == 2  # Both precursors should be identified

    def test_get_identified_precursor_intensities(self, mock_oswpq_dir):
        """Test getIdentifiedPrecursorIntensities method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        # Test for all runs
        intensities = access.getIdentifiedPrecursorIntensities(qvalue=0.01)
        assert isinstance(intensities, pd.DataFrame)
        assert 'Precursor' in intensities.columns
        assert 'Intensity' in intensities.columns
        assert 'runName' in intensities.columns
        
        # Test for specific run
        intensities_run = access.getIdentifiedPrecursorIntensities(qvalue=0.01, run='run1')
        assert isinstance(intensities_run, pd.DataFrame)
        assert 'Precursor' in intensities_run.columns
        assert 'Intensity' in intensities_run.columns

    def test_get_identified_proteins(self, mock_oswpq_dir):
        """Test getIdentifiedProteins method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        # Test for all runs
        proteins = access.getIdentifiedProteins(qvalue=0.01)
        assert isinstance(proteins, dict)
        
        # Test for specific run
        proteins_run = access.getIdentifiedProteins(qvalue=0.01, run='run1')
        assert isinstance(proteins_run, set)
        assert 'P12345' in proteins_run
        assert 'P67890' in proteins_run

    def test_get_identified_peptides(self, mock_oswpq_dir):
        """Test getIdentifiedPeptides method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        # Test for all runs
        peptides = access.getIdentifiedPeptides(qvalue=0.01)
        assert isinstance(peptides, dict)
        
        # Test for specific run
        peptides_run = access.getIdentifiedPeptides(qvalue=0.01, run='run1')
        assert isinstance(peptides_run, set)
        assert 'PEPTIDE' in peptides_run
        assert 'SEQUENCE' in peptides_run

    def test_get_transition_group_features(self, mock_oswpq_dir):
        """Test getTransitionGroupFeatures method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        features = access.getTransitionGroupFeatures('run1', 'PEPTIDE', 2)
        assert isinstance(features, list)
        assert len(features) == 1  # Should find one feature
        
        # Test non-existent peptide
        features_empty = access.getTransitionGroupFeatures('run1', 'NONEXISTENT', 2)
        assert len(features_empty) == 0

    def test_get_transition_group_features_df(self, mock_oswpq_dir):
        """Test getTransitionGroupFeaturesDf method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        features_df = access.getTransitionGroupFeaturesDf('run1', 'PEPTIDE', 2)
        assert isinstance(features_df, pd.DataFrame)
        
        # Should have expected columns
        expected_columns = ['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 
                          'consensusApex', 'consensusApexIntensity', 'consensusApexIM', 
                          'precursor_charge', 'sequence', 'software']
        for col in expected_columns:
            assert col in features_df.columns

    def test_get_top_transition_group_feature(self, mock_oswpq_dir):
        """Test getTopTransitionGroupFeature method"""
        access = OSWPQResultsAccess(mock_oswpq_dir)
        
        top_feature = access.getTopTransitionGroupFeature('run1', 'PEPTIDE', 2)
        assert top_feature is not None
        assert top_feature.sequence == 'PEPTIDE'
        assert top_feature.precursor_charge == 2
        
        # Test non-existent peptide
        top_feature_none = access.getTopTransitionGroupFeature('run1', 'NONEXISTENT', 2)
        assert top_feature_none is None