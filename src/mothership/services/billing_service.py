import random
from mothership.data.repository import GeneratorRepository
from mothership.core.utils import logger
from mothership.services.printer_delivery import printer_io

class BillingService:
    """
    Handles all logic related to recurring bills (Oxygen, etc.).
    """
    def __init__(self, generator_repo=None):
        self.generator_repo = generator_repo or GeneratorRepository()

    def print_oxygen_bill(self):
        """
        Sends an oxygen bill to the printer hardware with a random quote.
        """
        fortunes = self.generator_repo.get_fortunes_data()
        if not fortunes or not isinstance(fortunes, list):
            logger.error("Error: Could not read oxygen fortunes.")
            return False

        quote = random.choice(fortunes)
        
        payload = [
            "tmpl:tatourmi+mothership-oxygen-bill",
            {
                "id": "O2-01",
                "name": "OxygenTax",
                "data": {
                    "price": "100",
                    "quote": quote
                }
            },
            {}
        ]

        return printer_io.send_to_hardware(payload, description="Oxygen Bill")
