"""
massdash/main
~~~~~~~~~~~~~
"""

import click
import sys
import os
from streamlit.web import cli as stcli

@click.group(chain=True)
@click.version_option()
def cli():
    """
    MassDash: Streamlined DIA-MS visualization, analysis, optimization and rapid prototyping. 
    """

# GUI for MassDash.
@cli.command()
@click.option('--verbose', '-v', is_flag=True, help="Enables verbose mode.")
@click.option('--perf', '-t', is_flag=True, help="Enables measuring and tracking of performance.")
@click.option('--perf_output', '-o', default='MassDash_Performance_Report.txt', type=str, help="Name of the performance report file to writeout to.")
@click.option('--server_port', '-p', default=8501, type=int, help="Port to run the MassDash GUI on.")
def gui(verbose, perf, perf_output, server_port):
    """
    GUI for MassDash.
    """

    click.echo("Starting MassDash GUI...")
    if verbose:
        click.echo("Arguments:")
        for arg_name, arg_value in locals().items():
            if arg_name != 'self':  # Exclude 'self' for methods inside a class
                click.echo(f"{arg_name}: {arg_value}")
                
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'gui.py')
    
    add_args = []
    if verbose:
        add_args.append('--verbose')
    if perf:
        add_args.append('--perf')
    if perf_output and perf:
        add_args.append('--perf_output')
        add_args.append(perf_output)
        # if perf_out exists, get user to type y or n to delete the existing file
        if os.path.exists(perf_output):
            click.echo(f"Performance report file {perf_output} already exists.\nDo you want to overwrite it? [Y/n]")
            response = input()
            # Ensure that the user types in a valid response
            while response not in ['Y', 'n']:
                click.echo("Invalid response. Please type in Y or n.")
                response = input()
            if response == 'Y':
                os.remove(perf_output)
            else:
                click.echo("Exiting MassDash GUI...")
                sys.exit(0)
    streamlit_args = []
    if server_port:
        streamlit_args.append('--server.port')
        streamlit_args.append(str(server_port))
    if verbose:
        click.echo(f"Running: streamlit run {filename} {streamlit_args} -- {add_args}")
    sys.argv = ["streamlit", "run", filename, *streamlit_args, "--", *add_args]
    sys.exit(stcli.main())