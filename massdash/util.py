"""
massdash/util
~~~~~~~~~~~~~
"""

import os
import sys
import importlib
from typing import Optional, List
from pathlib import Path
from collections import Counter

# Logging and performance modules
from functools import wraps
import contextlib
from time import time, sleep
from timeit import default_timer
from datetime import timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
import psutil
import pyautogui

import requests
import streamlit as st
from streamlit.components.v1 import html


#######################################
## Logging Utils

# Logging
FORMATTER = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "MassDash.log"

def get_console_handler():
    """
    Returns a console handler for logging messages to the console.

    Returns:
        logging.StreamHandler: Console handler with the specified formatter.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler():
    """
    Returns a file handler for logging.

    Returns:
        file_handler (TimedRotatingFileHandler): File handler for logging.
    """
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name, log_level=logging.INFO):
    """
    Get a logger with the specified name.

    Args:
        logger_name (str): The name of the logger.

    Returns:
        logging.Logger: The logger object.

    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level) # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger

# Call first instance of logger
LOGGER = get_logger('MassDash')

@contextlib.contextmanager
def code_block_timer(ident, log_type):
    """
    A context manager that measures the execution time of a code block.

    Args:
        ident (str): Identifier for the code block.
        log_type (function): Logging function to output the elapsed time.

    Yields:
        None

    Example:
        with code_block_timer("my_code_block", logger.info):
            # Code block to measure execution time
            ...
    """
    tstart = time()
    yield
    elapsed = time() - tstart
    log_type("{0}: Elapsed {1} ms".format(ident, elapsed))

@contextlib.contextmanager
def time_block():
    """
    A context manager that measures the time it takes to execute a block of code.

    Usage:
    with time_block() as elapsed_time:
        # code block to be timed

    Returns:
    A timedelta object representing the elapsed time.
    """
    start = end = default_timer()
    yield lambda: timedelta(seconds=end - start)
    end = default_timer()

@contextlib.contextmanager
def measure_memory_block():
    """
    A context manager that measures the memory usage of a block of code.

    Usage:
    with measure_memory_block() as memory:
        # code block to be measured

    Returns:
    A float representing the memory usage in MB.
    """
    start_memory = psutil.virtual_memory().used
    yield lambda: (end_memory - start_memory) / 1024 ** 2
    end_memory = psutil.virtual_memory().used

class MeasureBlock:
    def __init__(self, metric_name: str=None, write_out_perf: bool=False, perf_output: str='MassDash_Performance_Report.txt'):
        self.metric_name = metric_name
        self.write_out_perf = write_out_perf
        self.perf_output = perf_output
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.execution_time = None
        self.memory_usage = None
        
    def __enter__(self):
        self.start_time = default_timer()
        self.start_memory = psutil.Process(os.getpid()).memory_info().rss
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = default_timer()
        self.end_memory = psutil.Process(os.getpid()).memory_info().rss
        self.execution_time = self.end_time - self.start_time
        self.memory_usage = (self.end_memory - self.start_memory) / (1024 ** 2)  # Convert bytes to megabytes
        # Open file and append data to it as tabular data
        if self.write_out_perf:
            # Check if there are headers in the file
            if not os.path.isfile(self.perf_output):
                with open(self.perf_output, 'w', encoding='utf-8') as f:
                    f.write('metric_name\texecution_time_sec\tmemory_usage_MB\n')
            # Write out the performance data
            with open(self.perf_output, 'a', encoding='utf-8') as f:
                f.write(f'{self.metric_name}\t{self.execution_time}\t{self.memory_usage}\n')


#######################################
## Data Handling Utils

def copy_attributes(source_instance, destination_instance):
    """
    Copies attributes from the source instance to the destination instance.

    Args:
        source_instance: The object from which attributes will be copied.
        destination_instance: The object to which attributes will be copied.

    Returns:
        None
    """
    # Iterate over attributes of the source instance
    for attr_name, attr_value in vars(source_instance).items():
        # Set the attribute in the destination instance
        setattr(destination_instance, attr_name, attr_value)

def check_streamlit():
    """
    Function to check whether python code is run within streamlit

    Returns
    -------
    use_streamlit : boolean
        True if code is run within streamlit, else False
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if not get_script_run_ctx():
            use_streamlit = False
        else:
            use_streamlit = True
    except ModuleNotFoundError:
        use_streamlit = False
    return use_streamlit

def check_sqlite_table(con, table):
    """
    Check if a table exists in a SQLite database.

    Args:
        con (sqlite3.Connection): Connection object to the SQLite database.
        table (str): Name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    table_present = False

    result = con.execute('SELECT count(name) FROM sqlite_master WHERE type="table" AND name=?', (table,))

    if result.fetchone()[0] == 1:
        table_present = True

    return table_present

def check_sqlite_column_in_table(con, table, column):
    """
    Check if a column exists in a SQLite table.

    Args:
        con (sqlite3.Connection): Connection object to the SQLite database.
        table (str): Name of the table to check.
        column (str): Name of the column to check.

    Returns:
        bool: True if the column exists, False otherwise.
    """
    column_present = False
    c = con.cursor()
    c.execute('SELECT count(name) FROM pragma_table_info("%s") WHERE name="%s"' % (table, column))
    if c.fetchone()[0] == 1:
        column_present = True
    else:
        column_present = False
    c.fetchall()

    return(column_present)

def check_package(package_name: str, module_path: Optional[str]=None):
    """
    Check if a Python package is installed.

    Args:
        package_name (str): The name of the package to check.
        module_path (str, optional): The path to the module within the package. Defaults to None.

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    try:
        if module_path is None:
            return importlib.import_module(package_name), True
        else:
            return importlib.import_module(f"{package_name}.{module_path}"), True
    except ImportError:
        print(f"{package_name} is not installed. Please install it using 'pip install {package_name}'.")
        return None, False

def check_function(package_name: str, function_name: str, module_path: Optional[str]=None):
    """
    Check if a function is available in a Python package.

    Args:
        package_name (str): The name of the package to check.
        function_name (str): The name of the function to check.
        module_path (str, optional): The path to the module within the package. Defaults to None.

    Returns:
        bool: True if the function is available, False otherwise.
    """
    try:
        if module_path is None:
            module = importlib.import_module(package_name)
        else:
            module = importlib.import_module(f"{package_name}.{module_path}")
        return getattr(module, function_name), True
    except ImportError:
        print(f"{package_name} is not installed. Please install it using 'pip install {package_name}'.")
        return None, False

def file_basename_without_extension(file_path):
    """
    Returns the basename of a file without the extension including archive extensions.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Basename of the file without the extension.
    """
    # Get the base name of the file
    base_name = os.path.basename(file_path)
    
    # Remove known archive extensions (gz, xz, tar, etc.)
    archive_extensions = ['.gz', '.xz', '.tar', '.zip', '.rar', '.7z']
    for ext in archive_extensions:
        if base_name.endswith(ext):
            base_name = base_name[:-len(ext)]
    
    # Remove other extensions
    base_name, _ = os.path.splitext(base_name)
    
    return base_name

def infer_unique_filenames(filenames: List, sep: str='_'):
    """
    Infer unique filenames by removing substrings that occur in all filenames.

    Args:
        filenames (list): A list of filenames.
        sep (str, optional): The separator used to split filenames into parts. Defaults to '_'.

    Returns:
        dict: A dictionary mapping original filenames to the filtered filenames.
    """
    if len(filenames) == 1:
        return {filenames[0]: filenames[0]}
    
    # Create dictionary mapping filenames to their parts
    filename_dict = {filename: filename.split(sep) for filename in filenames}

    # Flatten the list of substrings
    all_substrings = [substring for sublist in filename_dict.values() for substring in sublist]

    # Count occurrences of each substring
    substring_counts = Counter(all_substrings)

    # Get the total number of filenames
    total_files = len(filenames)

    # Remove substrings that occur in all filenames
    remove_substrings = [substring for substring, count in substring_counts.items() if count == total_files]

    # Pop substrings from filename_dict
    for filename in filename_dict:
        filename_dict[filename] = [substring for substring in filename_dict[filename] if substring not in remove_substrings]

    # Join the remaining substrings and maintain mapping to original filenames in dict
    filtered_filenames = {filename: sep.join(substrings) for filename, substrings in filename_dict.items()}

    return filtered_filenames

def get_download_folder():
    """
    Get the download folder based on the user's operating system.

    Returns:
        str: The path to the download folder.
    """
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "Downloads")

def download_file(url: str, dest_folder: str):
    """
    Downloads a file from the given URL and saves it to the specified destination folder.

    Args:
        url (str): The URL of the file to download.
        dest_folder (str): The destination folder where the file will be saved.

    Returns:
        None
    """
    os.makedirs(dest_folder, exist_ok=True)
    response = requests.get(url)
    filename = url.split("/")[-1]
    if check_streamlit():
        import streamlit as st
        with st.spinner(f"Downloading {url} to {dest_folder}"):
            with open(os.path.join(dest_folder, filename), "wb") as f:
                f.write(response.content)
    else:
        LOGGER.info(f"Downloading {url} to {dest_folder}")
        with open(os.path.join(dest_folder, filename), "wb") as f:
            f.write(response.content)

def rgb_to_hex(rgb):
    """
    Converts an RGB color value to its corresponding hexadecimal representation.

    Args:
        rgb (tuple): A tuple containing the RGB values as floats between 0 and 1.

    Returns:
        str: The hexadecimal representation of the RGB color.

    Example:
        >>> rgb_to_hex((0.5, 0.75, 1.0))
        '#7fbfff'
    """
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))


def open_page(url: str):
    """
    Opens a new browser window/tab with the specified URL.

    Args:
        url (str): The URL to open in the new window/tab.
    """
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)

def reset_app():
    """
    Resets the application by clearing cache data and resources, and resetting session state variables.
    """
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.WELCOME_PAGE_STATE = True
    st.session_state.workflow = None
    # set everything to unclicked
    for k in st.session_state.clicked.keys():
        st.session_state.clicked[k] = False

def close_app():
    """
    Closes the MassDash app by terminating the Streamlit process and closing the browser tab.
    """
    # Give a bit of delay for user experience
    sleep(5)
    # Close streamlit browser tab
    LOGGER.info("Closing MassDash app browser tab...")
    pyautogui.hotkey('ctrl', 'w')
    # Terminate streamlit python process
    pid = os.getpid()
    LOGGER.info(f"Terminating MassDash app process with PID: {pid}")
    p = psutil.Process(pid)
    p.terminate()

#######################################
## Decorators

class conditional_decorator(object):
    """
    A decorator that applies another decorator to a function only if a condition is met.
    See: https://gist.github.com/T1T4N/22ca7b0764cefe917b2b3a6bb056364c

    Args:
        dec (function): The decorator to apply.
        condition (bool): The condition that must be met for the decorator to be applied.

    Returns:
        function: The decorated function, or the original function if the condition is not met.
    """
    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)

def method_timer(f):
    """
    Decorator that measures the execution time of a method.

    Args:
        f (function): The method to be timed.

    Returns:
        function: The wrapped method.

    """
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logging.debug('method:%r args:[%r, %r] took: %2.4f sec' % (
            f.__name__, args, kw, te-ts))
        return result
    return wrap

def find_git_directory(start_path=None):
    """Find the full path to the nearest '.git' directory by climbing up the directory tree.

    Args:
        start_path (str or Path, optional): The starting path for the search. If not provided,
            the current working directory is used.

    Returns:
        Path or None: The full path to the '.git' directory if found, or None if not found.
    """
    # If start_path is not provided, use the current working directory
    start_path = Path(start_path) if start_path else Path.cwd()
    # Iterate through parent directories until .git is found
    current_path = start_path
    while current_path:
        git_path = current_path / '.git'
        if git_path.is_dir():
            return git_path.resolve()
        current_path = current_path.parent

    # If .git is not found in any parent directory, return None
    return None
