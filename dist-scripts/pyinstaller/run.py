# This file is the entry point for the application when it is run as a standalone executable.
if __name__ == "__main__":
    try:
        import os
        import massdash.main
        from massdash.util import get_free_port
        if sys.platform[:6] == "darwin":
	        os.environ['KMP_DUPLICATE_LIB_OK']='True'
        use_port = "8509" # str(get_free_port())
        massdash.main.gui(['--verbose', '--server_port', use_port, '--no_global_developmentMode', '--no_browser_gatherUsageStats'], standalone_mode=False)
    except ImportError:
        import sys
        import traceback
        traceback.print_exception(*sys.exc_info())
        input("An error occurred. Press Enter to exit.")