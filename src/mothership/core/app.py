import threading
import time
from mothership.core.utils import logger

class ApiWorker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self.interval = 20 # Default to 20 minutes
        self.is_running = False
        self.api_url = None # Placeholder if we want to make the URL configurable later
        self.start_time = 0
        self.total_seconds = 0
        self.next_trigger_time = 0
        self.remaining_on_stop = 0
        self._task_callback = None

    def set_task(self, callback):
        """Sets the function to be executed when the timer ticks."""
        self._task_callback = callback

    @property
    def remaining_seconds(self) -> float:
        if not self.is_running:
            return self.remaining_on_stop
        if self.next_trigger_time == 0:
            return 0.0
        return max(0.0, self.next_trigger_time - time.time())

    @property
    def progress(self) -> float:
        if self.total_seconds <= 0:
            return 0.0
        
        # If running and next_trigger_time is 0, we are in the middle of a task
        if self.is_running and self.next_trigger_time == 0:
            return 1.0
            
        rem = self.remaining_seconds
        elapsed = self.total_seconds - rem
        return min(max(0.0, elapsed / self.total_seconds), 1.0)

    def _run_loop(self):
        logger.log(f"Timer started. Interval: {self.interval}m")
        self.total_seconds = self.interval * 60

        while not self._stop_event.is_set() and self.is_running:
            # Phase 1: Wait Loop
            while time.time() < self.next_trigger_time and not self._stop_event.is_set() and self.is_running:
                time.sleep(0.5)

            if self._stop_event.is_set() or not self.is_running:
                break
            
            # Phase 2: Action Phase
            self.next_trigger_time = 0
            
            if self._task_callback:
                try:
                    self._task_callback()
                except Exception as e:
                    logger.error(f"Timer Task: Execution failed - {e}")
            else:
                logger.warning("Timer Tick: No task callback configured.")

            if self._stop_event.is_set() or not self.is_running:
                break

            # Schedule next
            self.next_trigger_time = time.time() + self.total_seconds

        logger.log("Timer loop stopped.")

    def start(self, interval=None, api_url=None):
        if self.is_running:
            logger.log("Warning: Timer is already running.")
            return False

        if interval:
            try:
                self.interval = int(interval)
                self.remaining_on_stop = 0 # Force reset if interval changed
            except ValueError:
                logger.log(f"Invalid interval format: {interval}")
                return False
            
        if api_url:
            self.api_url = api_url

        self.total_seconds = self.interval * 60
        self.is_running = True
        
        # Resume or Start New
        if self.remaining_on_stop > 0:
            self.next_trigger_time = time.time() + self.remaining_on_stop
            self.remaining_on_stop = 0
        else:
            self.next_trigger_time = time.time() + self.total_seconds

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        if not self.is_running:
            logger.log("Warning: Timer is not running.")
            return False

        # Save current progress
        self.remaining_on_stop = self.remaining_seconds
        self.is_running = False
        self.next_trigger_time = 0
        self._stop_event.set()
        return True


class TimerManager:
    """Manages multiple named ApiWorker instances."""
    def __init__(self):
        self._workers = {}

    def register(self, name: str, interval: int = 20):
        """Registers a new named worker."""
        if name not in self._workers:
            worker = ApiWorker()
            worker.interval = interval
            self._workers[name] = worker
            return worker
        return self._workers[name]

    def get(self, name: str) -> ApiWorker:
        """Retrieves a named worker."""
        return self._workers.get(name)

    def list_names(self) -> list[str]:
        """Returns all registered timer names."""
        return list(self._workers.keys())

# Global instance to be shared across the application
timer_manager = TimerManager()
