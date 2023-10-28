import os
import glob
import base64

# streamlit components
import streamlit as st

# Type hinting
from typing import List, Tuple

# Common environment variables
PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORKING_FOLDER = os.getcwd()
MASSPEC_FILE_FORMATS = ["mzML", "mzXML", "raw", "wiff", "d"]

PEAK_PICKING_ALGORITHMS = ["PeakPickerMRM"]

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
