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
@click.option('--verbose', '-v', is_flag=True, help="Enables verbose mode.")
@click.option('--perf', '-t', is_flag=True, help="Enables measuring and tracking of performance.")
@click.option('--perf_output', '-o', default='MassSeer_Performance_Report.txt', type=str, help="Name of the performance report file to writeout to.")
def gui(verbose, perf, perf_output):
    """
    GUI for MassSeer.
    """

    click.echo("Starting MassSeer GUI...")
    click.echo("Arguments:")
    click.echo(f"verbose: {verbose}")
    click.echo(f"perf: {perf}")
    click.echo(f"perf_output: {perf_output}")
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
                click.echo("Exiting MassSeer GUI...")
                sys.exit(0)
                
    print(f"Running: streamlit run {filename} {add_args}")
    sys.argv = ["streamlit", "run", filename, "--", *add_args]
    sys.exit(stcli.main())