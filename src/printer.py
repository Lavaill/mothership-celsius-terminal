import urllib.request
import urllib.error
import json
from src.utils import logger

class Printer:
    """
    A pure I/O service responsible only for delivering finalized payloads to the printer hardware.
    It does not know about "Wounds", "Missions", or "Mothership" logic.
    """
    def __init__(self, printer_url="http://127.0.0.1:7123/api/printTemplate"):
        self.printer_url = printer_url

    def send_to_hardware(self, payload, description="document"):
        """
        Sends a JSON payload to the printer API.
        """
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.printer_url, data=data, headers={'Content-Type': 'application/json'})
            
            logger.info(f"Delivering {description} to hardware...")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    logger.info(f"Successfully printed {description}.")
                    return True
                else:
                    logger.error(f"Hardware error printing {description}. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.error(f"Hardware error printing {description}. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            return False
        except Exception as e:
            logger.error(f"Connection error to printer hardware: {e}")
            return False

# Global instance for hardware delivery
printer_io = Printer()
