import os
import sys

# Logging and performance modules
from functools import wraps
import contextlib
from time import time
from timeit import default_timer
from datetime import timedelta
import logging
from logging.handlers import TimedRotatingFileHandler



#######################################
## Logging Utils

# Logging
FORMATTER = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "MassSeer.log"

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
LOGGER = get_logger('MassSeer')

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
    c = con.cursor()
    c.execute('SELECT count(name) FROM sqlite_master WHERE type="table" AND name="%s"' % table)
    if c.fetchone()[0] == 1:
        table_present = True
    else:
        table_present = False
    c.fetchall()

    return(table_present)

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

