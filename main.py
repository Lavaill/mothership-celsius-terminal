import sys
import os

# Ensure the 'src' directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import threading
import traceback
# Import utils first to ensure exception hooks are registered immediately
from mothership.core.utils import logger
from mothership.ui.server import run_server
from mothership.ui.tui import MothershipApp

if __name__ == '__main__':
    logger.info("--- Application Startup ---")
    try:
        # Start the API Server in a separate thread
        logger.info("Starting API Server thread...")
        api_thread = threading.Thread(target=run_server, args=(8000,), daemon=True)
        api_thread.start()

        # Start the TUI
        logger.info("Initializing TUI App...")
        app = MothershipApp()
        logger.info("Running TUI App...")
        app.run()
    except BaseException as e:
        logger.critical("Fatal error in main execution", exc_info=True)
        traceback.print_exc()
        sys.exit(1)