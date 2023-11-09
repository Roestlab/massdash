import os
import sys
import glob
import base64
import click
import ast

# Logging and performance modules
from functools import wraps
import contextlib
from time import time
from timeit import default_timer 
from datetime import datetime, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler


# Type hinting
from typing import List, Tuple

# Common environment variables
MASSPEC_FILE_FORMATS = ["mzML", "mzXML", "raw", "wiff", "d"]

# Logging
FORMATTER = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "MassSeer.log"

# Alorithms
PEAK_PICKING_ALGORITHMS = ["OSW-PyProphet","PeakPickerMRM"]


# Common methods

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


def method_timer(f):
    """
    A decorator that logs the time taken by a method to execute.

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

@contextlib.contextmanager
def code_block_timer(ident, log_type):
    """
    A context manager that logs the elapsed time of a code block.

    Args:
        ident (str): A string identifier for the code block.
        log_type (function): A logging function that takes a string message as input.

    Yields:
        None

    Example:
        >>> with code_block_timer("my_code_block", print):
        ...     # some code to be timed
        my_code_block: Elapsed 0.123456789 ms
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

def get_console_handler():
    """
    Returns a console handler for logging messages to the console.

    Returns:
    console_handler (logging.StreamHandler): A console handler with the specified formatter.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler():
    """
    Returns a file handler for logging to a file with a rotating filename based on the current date.
    """
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
   """
   Returns a logger object with the specified name and configured with a console and file handler.
   
   Args:
       logger_name (str): The name of the logger object.
       
   Returns:
       logger (logging.Logger): The logger object with the specified name and handlers.
   """
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

# Logger needs to initiated once
LOGGER = get_logger('MassSeer')

