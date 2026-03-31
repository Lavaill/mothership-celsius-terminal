from mothership.data.repository import GeneratorRepository
from mothership.core.dice import DiceRoller
from mothership.core.utils import logger
from mothership.services.printer_delivery import printer_io

class WoundService:
    """
    Handles all logic related to generating and formatting wound reports.
    """
    def __init__(self, generator_repo=None):
        self.generator_repo = generator_repo or GeneratorRepository()

    def get_wound_types(self):
        """
        Returns a list of available wound types (for TUI autocomplete).
        """
        wounds_data = self.generator_repo.get_wounds_data()
        if not wounds_data or "wound-tables" not in wounds_data:
            return []
        
        return [table["type"] for table in wounds_data["wound-tables"]]

    def print_wound(self, wound_type, wound_number=None):
        """
        Generates and sends a wound payload to the printer hardware.
        """
        wounds_data = self.generator_repo.get_wounds_data()
        if not wounds_data:
            logger.error("Error: Could not read wounds data.")
            return False

        # Find the correct table
        target_table = None
        for table in wounds_data.get("wound-tables", []):
            if table["type"].upper() == wound_type.upper():
                target_table = table
                break
        
        if not target_table:
            logger.error(f"Error: Wound type '{wound_type}' not found.")
            return False

        # Determine wound number (1d10)
        if wound_number is None:
            wound_number = DiceRoller.roll(10)
        else:
            try:
                wound_number = int(wound_number)
                if not (1 <= wound_number <= 10):
                    raise ValueError
            except ValueError:
                logger.error(f"Error: Invalid wound number '{wound_number}'. Must be 1-10.")
                return False

        # Get severity and description
        severity_map = wounds_data.get("wound-severity", {})
        severity = severity_map.get(str(wound_number), "Unknown Severity")
        description = target_table.get(str(wound_number), "Unknown Description")

        payload = [
            "tmpl:tatourmi+mothership-wound",
            {
                "id": "mothership-wound",
                "name": "mothership-wound",
                "data": {
                    "severity": severity,
                    "type": wound_type.upper(),
                    "desc": description
                }
            },
            {}
        ]
        
        return printer_io.send_to_hardware(payload, description=f"Wound Report: {wound_type} {wound_number}")
