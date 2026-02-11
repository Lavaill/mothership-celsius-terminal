import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "mothership.log")

# Wipe log file on startup to ensure clean debugging
if os.path.exists(LOG_FILE):
    try:
        os.remove(LOG_FILE)
    except Exception as e:
        print(f"Warning: Could not wipe log file: {e}")

print(f"DEBUG: Logging to {LOG_FILE}")

class TuiHandler(logging.Handler):
    """Custom logging handler to send logs to the TUI via callback."""
    def __init__(self):
        super().__init__()
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def emit(self, record):
        if self.callback:
            try:
                msg = self.format(record)
                self.callback(msg)
            except Exception:
                self.handleError(record)

class LoggerWrapper:
    def __init__(self):
        self._logger = logging.getLogger("Mothership")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        # 1. File Handler (Detailed, Persistent, Rotating)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(threadName)s - %(filename)s:%(lineno)d - %(message)s')
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

        # 2. TUI Handler (User-facing)
        self.tui_handler = TuiHandler()
        # Simple format for the UI - REMOVED COLORS
        tui_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.tui_handler.setFormatter(tui_formatter)
        # Only show INFO and above in the TUI (hides DEBUG logs with filenames)
        self.tui_handler.setLevel(logging.INFO)
        self._logger.addHandler(self.tui_handler)

    def set_callback(self, callback):
        self.tui_handler.set_callback(callback)

    # --- Proxy Methods ---
    def log(self, message):
        """Legacy support: maps to INFO."""
        self._logger.info(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message, exc_info=True):
        self._logger.error(message, exc_info=exc_info)

    def debug(self, message):
        self._logger.debug(message)

    def critical(self, message, exc_info=True):
        self._logger.critical(message, exc_info=exc_info)

logger = LoggerWrapper()

# --- Global Exception Handling ---
# This ensures that if the program crashes, the stack trace is written to the log file.
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    except Exception:
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

sys.excepthook = handle_exception

# Handle thread exceptions (Python 3.8+)
if hasattr(threading, 'excepthook'):
    def handle_thread_exception(args):
        if args.exc_type == KeyboardInterrupt:
            return
        logger.error(f"Uncaught exception in thread: {args.thread.name}", 
                     exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
    threading.excepthook = handle_thread_exception