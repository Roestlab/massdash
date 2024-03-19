# This file is the entry point for the application when it is run as a standalone executable.
if __name__ == "__main__":
    try:
        import massdash.main
        massdash.main.gui(['--verbose', '--server_port', '8501', '--no_global_developmentMode', '--no_browser_gatherUsageStats'], standalone_mode=False)
    except ImportError:
        import sys
        import traceback
        traceback.print_exception(*sys.exc_info())
        input("An error occurred. Press Enter to exit.")