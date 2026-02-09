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
        self.start_time = 0
        self.total_seconds = 0

    @property
    def progress(self) -> float:
        if not self.is_running or self.total_seconds == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        return min(elapsed / self.total_seconds, 1.0)

    def _run_loop(self):
        logger.info(f"Timer started. Interval: {self.interval}s")
        self.total_seconds = self.interval * 60
        self.is_running = True # Set True LAST to prevent race condition in progress calculation

        while not self._stop_event.is_set():
            self.start_time = time.time()
            # --- SIMULATE API CALL ---
            try:
                # Call the oxygen bill printer service
                printer_service.print_oxygen_bill()
            except Exception as e:
                logger.error(f"API Call: Failed", exc_info=True)

            # Granular wait to allow for progress tracking and faster stopping
            end_wait = time.time() + self.total_seconds
            while time.time() < end_wait and not self._stop_event.is_set():
                time.sleep(1)

        self.is_running = False
        logger.info("Timer loop stopped.")

    def start(self, interval=None, api_url=None):
        if self.is_running:
            logger.warning("Timer is already running.")
            return False

        if interval:
            try:
                self.interval = int(interval)
            except ValueError:
                logger.error(f"Invalid interval format: {interval}")
                return False
            
        if api_url:
            self.api_url = api_url

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        if not self.is_running:
            logger.warning("Timer is not running.")
            return False

        self._stop_event.set()
        # We don't join() here to avoid blocking the HTTP server response
        return True


# Global instance to be shared between CLI and HTTP Server
logger.info("Initializing API Worker...")
worker = ApiWorker()
logger.info("API Worker initialized.")
