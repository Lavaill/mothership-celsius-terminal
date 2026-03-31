import pytest
import os
import sys
from unittest.mock import MagicMock

# Ensure the 'src' directory is in the Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

@pytest.fixture(autouse=True, scope="session")
def printer_safety_lock():
    """
    GLOBAL SAFETY LOCK:
    Mocks 'mothership.services.printer_delivery.Printer.send_to_hardware' 
    at the start of the test session to ensure no actual network calls 
    are made to the physical printer.
    """
    from mothership.services.printer_delivery import Printer
    
    # Replace the actual method with a mock
    # This ensures that even if a developer (or AI) forgets to mock it locally, 
    # the test will not send anything to the printer.
    original_method = Printer.send_to_hardware
    Printer.send_to_hardware = MagicMock(return_value=True)
    
    yield Printer.send_to_hardware
    
    # Restore it just in case after the session (though usually not necessary)
    Printer.send_to_hardware = original_method
