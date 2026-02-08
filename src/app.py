import threading
import time
from src.utils import logger
from src.printer import printer_service

class ApiWorker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self.interval = 5
        self.is_running = False
        self.api_url = None # Placeholder if we want to make the URL configurable later

    def _run_loop(self):
        logger.log(f"Timer started. Interval: {self.interval}s")
        self.is_running = True

        while not self._stop_event.is_set():
            # --- SIMULATE API CALL ---
            try:
                # Call the oxygen bill printer service
                printer_service.print_oxygen_bill()
            except Exception as e:
                logger.log(f"API Call: Failed - {e}")

            # Wait for interval OR stop signal
            self._stop_event.wait(self.interval * 60) # Interval is in minutes

        self.is_running = False
        logger.log("Timer loop stopped.")

    def start(self, interval=None, api_url=None):
        if self.is_running:
            logger.log("Warning: Timer is already running.")
            return False

        if interval:
            self.interval = int(interval)
            
        if api_url:
            self.api_url = api_url

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
