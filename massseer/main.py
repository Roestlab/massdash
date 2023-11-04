import click
import sys
import os
from streamlit.web import cli as stcli

@click.group(chain=True)
@click.version_option()
def cli():
    """
    MassSeer: Streamlined DIA-MS visualization, analysis, optimization and rapid prototyping. 
    """

# GUI for MassSeer.
@cli.command()
def gui():
    """
    GUI for MassSeer.
    """

    click.echo("Starting MassSeer GUI...")
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'gui.py')
    sys.argv = ["streamlit", "run", filename]
    sys.exit(stcli.main())