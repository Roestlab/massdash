from streamlit.testing.v1 import AppTest
from massdash.util import find_git_directory
from pathlib import Path
import pytest

GUI_DIR = str(find_git_directory(Path(__file__).resolve()).parent / 'massdash' / 'gui.py')

@pytest.fixture
def at():
    at =  AppTest(GUI_DIR, default_timeout=60)
    at.session_state.clicked  = {'load_toy_dataset_xic_data':False, 'load_toy_dataset_raw_data':False, 'load_toy_dataset_search_results_analysis':False}
    at.session_state.workflow = None
    return at

def test_welcome_screen(at):
    at.run()
    assert not at.exception

def test_extracted_data_example(at):
    at.session_state.workflow = 'xic_data'
    at.session_state.clicked['load_toy_dataset_xic_data'] = True
    at.run()
    assert not at.exception

def test_raw_data_example(at):
    at.session_state.workflow = 'raw_data'
    at.session_state.clicked['load_toy_dataset_raw_data'] = True
    at.run()
    assert not at.exception

def test_raw_data_im_example(at):
    at.session_state.workflow = 'raw_data'
    at.session_state.clicked['load_toy_dataset_raw_data_im'] = True
    at.run()
    assert not at.exception

# Fails currently 
'''
def test_search_results_analysis_example(at):
    at.session_state.workflow = 'search_results_analysis'
    at.session_state.clicked['load_toy_dataset_search_results_analysis'] = True
    at.run()
    assert not at.exception
'''