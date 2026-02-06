import threading
import time
from src.utils import logger

class ApiWorker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self.interval = 5
        self.is_running = False

    def _run_loop(self):
        logger.log(f"Timer started. Interval: {self.interval}s")
        self.is_running = True

        while not self._stop_event.is_set():
            # --- SIMULATE API CALL ---
            try:
                # In real life: response = requests.get(...)
                # if response.ok: logger.log("API Success")
                time.sleep(0.5)  # Simulate network delay
                logger.log("API Call: Success (200 OK)")
            except Exception as e:
                logger.log(f"API Call: Failed - {e}")

            # Wait for interval OR stop signal
            self._stop_event.wait(self.interval)

        self.is_running = False
        logger.log("Timer loop stopped.")

    def start(self, interval=None):
        if self.is_running:
            logger.log("Warning: Timer is already running.")
            return False

        if interval:
            self.interval = int(interval)

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        if not self.is_running:
            logger.log("Warning: Timer is not running.")
            return False

        self._stop_event.set()
        # We don't join() here to avoid blocking the HTTP server response
        return True


# Global instance to be shared between CLI and HTTP Server
worker = ApiWorker()