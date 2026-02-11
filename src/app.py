import threading
import time
from src.utils import logger
from src.printer import printer_service
from src.interface import Interface

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
        # Modulo to handle the loop nature
        # Actually, the loop resets start_time every iteration.
        # But we need to handle the case where we are waiting.
        return min(elapsed / self.total_seconds, 1.0)

    def _run_loop(self):
        logger.log(f"Timer started. Interval: {self.interval}m")
        self.total_seconds = self.interval * 60
        self.is_running = True

        while not self._stop_event.is_set():
            self.start_time = time.time()
            
            # Granular wait to allow for progress tracking and faster stopping
            # We wait BEFORE the action? Or AFTER?
            # Usually a timer waits then acts.
            # The previous code acted then waited.
            # "Make code that sends this post request for every single file... if receiving the command print contracts"
            # "Our timer makes an API call every X minutes."
            
            # Let's wait first, then act. Or act then wait?
            # "calls the oxygen-bill API every tick"
            # Usually implies wait -> act -> wait -> act.
            # But let's stick to the previous logic: Act (maybe initially?) then wait.
            # The previous logic was: Act, then wait.
            
            try:
                # Call the oxygen bill printer service
                printer_service.print_oxygen_bill()
            except Exception as e:
                logger.log(f"API Call: Failed - {e}")

            # Wait loop
            end_wait = time.time() + self.total_seconds
            while time.time() < end_wait and not self._stop_event.is_set():
                time.sleep(0.5) # Update frequency

        self.is_running = False
        logger.log("Timer loop stopped.")

    def start(self, interval=None, api_url=None):
        if self.is_running:
            logger.log("Warning: Timer is already running.")
            return False

        if interval:
            try:
                self.interval = int(interval)
            except ValueError:
                logger.log(f"Invalid interval format: {interval}")
                return False
            
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
        return True


# Global instance to be shared between CLI and HTTP Server
worker = ApiWorker()
