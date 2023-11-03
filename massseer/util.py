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
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# streamlit components
import streamlit as st

# Type hinting
from typing import List, Tuple

import pyopenms as po

# Common environment variables
PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORKING_FOLDER = os.getcwd()
MASSPEC_FILE_FORMATS = ["mzML", "mzXML", "raw", "wiff", "d"]

# Logging
FORMATTER = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "MassSeer.log"

# Alorithms
PEAK_PICKING_ALGORITHMS = ["OSW-PyProphet","PeakPickerMRM"]


# Common methods
def get_data_folder():
    return os.path.join(PROJECT_FOLDER, "data")

def get_input_folder():
    return os.path.join(get_data_folder(), "input")

def get_output_folder():
    return os.path.join(get_data_folder(), "output")

# @st.cache_data()
def get_base64_of_bin_file(png_file):
    """Convert a binary file to the corresponding base64 representation"""
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


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

def setCompressionOptions(opt):
    """
    Adds suitable compression options for an object of type
    pyopenms.PeakFileOptions
        - compresses mass / time arrays with numpress linear
        - compresses intensity with slof (log integer)
        - compresses ion mobility with slof (log integer)
    """
    cfg = po.NumpressConfig()
    cfg.estimate_fixed_point = True
    cfg.numpressErrorTolerance = -1.0 # skip check, faster
    cfg.setCompression(b"linear");
    cfg.linear_fp_mass_acc = -1; # set the desired RT accuracy in seconds
    opt.setNumpressConfigurationMassTime(cfg)
    cfg = po.NumpressConfig()
    cfg.estimate_fixed_point = True
    cfg.numpressErrorTolerance = -1.0 # skip check, faster
    cfg.setCompression(b"slof");
    opt.setNumpressConfigurationIntensity(cfg)
    opt.setCompression(True) # zlib compression

    # Now also try to compress float data arrays (this is not enabled in all
    # versions of pyOpenMS).
    try:
        cfg = po.NumpressConfig()
        cfg.estimate_fixed_point = True
        cfg.numpressErrorTolerance = -1.0 # skip check, faster
        cfg.setCompression(b"slof");
        opt.setNumpressConfigurationFloatDataArray(cfg)
    except Exception:
        pass

def method_timer(f):
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
    tstart = time()
    yield
    elapsed = time() - tstart
    log_type("{0}: Elapsed {1} ms".format(ident, elapsed))

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

def check_im_array(im_array):
    '''
    Check Ion Mobility Array to make sure values are valid
    '''
    
    if any(im_array<0):
      raise click.ClickException(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: There are values below 0 in the input ion mobility array! {im_array[im_array<0]}. Most likely a pyopenms memory view issue.")
    elif 'e' in str(im_array):
      raise click.ClickException(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: The input ion mobility array seems to be in scientific notation! {im_array}. Most likely a pyopenms memory view issue.")

def type_cast_value(value):
    '''
    Convert a string value to python literal
    '''
    if not isinstance(value, str):  # required for Click>=8.0.0
        return value
    try:
        return ast.literal_eval(value)
    except Exception:
        raise click.BadParameter(value)

def argument_value_log(args_dict):
    '''
    Print argument and value
    '''
    logging.debug("---------------- Input Parameters --------------------------")
    for key, item in args_dict.items():
        logging.debug(f"Parameter: {key} = {item}")
    logging.debug("------------------------------------------------------------\n")
