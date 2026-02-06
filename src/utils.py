import threading
import sys

# --- 1. Thread-Safe Logging ---
# This prevents background logs from messing up your typing prompt
class Logger:
    def __init__(self):
        self.lock = threading.Lock()

    def log(self, message):
        with self.lock:
            # \r moves cursor to start of line, clearing current input visually
            # This is a simple trick; for complex TUIs, use libraries like 'textual'
            sys.stdout.write(f'\r[Log] {message}\n')
            sys.stdout.write('(game-helper) > ') # Reprint prompt
            sys.stdout.flush()

logger = Logger()