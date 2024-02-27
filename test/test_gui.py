from streamlit.testing.v1 import AppTest
from massdash.util import find_git_directory
from pathlib import Path

MASSDASH_DIR = find_git_directory(Path(__file__).resolve()).parent / 'massdash'

def test_welcome_screen():
    at = AppTest.from_file("../massdash/gui.py", default_timeout=60).run()
    assert not at.exception