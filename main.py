import sys
import threading
# Import utils first to ensure exception hooks are registered immediately
from src.utils import logger
from src.server import run_server
from src.tui import MothershipApp

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
    except Exception as e:
        logger.critical("Fatal error in main execution", exc_info=True)
        sys.exit(1)