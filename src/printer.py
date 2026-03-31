import urllib.request
import urllib.error
import json
import os
import random
from src.jsonParser import JsonParser
from src.utils import logger
from src.dice import DiceRoller
from src.repository import MissionRepository, GeneratorRepository

class Printer:
    def __init__(self):
        self.parser = JsonParser()
        self.mission_repo = MissionRepository()
        self.generator_repo = GeneratorRepository()
        self.printer_url = "http://127.0.0.1:7123/api/printTemplate"

    def get_available_mission_ids(self):
        """
        Returns a list of all available mission IDs from the repository.
        """
        return self.mission_repo.get_all_mission_ids()

    def get_wound_types(self):
        """
        Returns a list of available wound types from the repository.
        """
        wounds_data = self.generator_repo.get_wounds_data()
        if not wounds_data or "wound-tables" not in wounds_data:
            return []
        
        return [table["type"] for table in wounds_data["wound-tables"]]

    def print_contract(self, mission_id):
        """
        Finds the mission by ID and sends its contract data to the printer.
        """
        return self._print_entry(mission_id, "contract")

    def print_mission(self, mission_id):
        """
        Finds the mission by ID and sends its mission data to the printer.
        """
        return self._print_entry(mission_id, "mission")

    def print_all_contracts(self):
        """
        Sends all contracts from active missions to the printer.
        """
        active_missions = self.mission_repo.get_active_missions()
        success_count = 0
        for mission_data, file_path in active_missions:
            if self._send_print_request(mission_data, file_path, "contract"):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(active_missions)} contracts to printer.")
        return success_count > 0

    def print_oxygen_bill(self):
        """
        Sends an oxygen bill to the printer with a random quote.
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

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.printer_url, data=data, headers={'Content-Type': 'application/json'})
            
            logger.info("Sending oxygen bill to printer...")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    logger.info("Successfully sent oxygen bill to printer.")
                    return True
                else:
                    logger.error(f"Failed to print oxygen bill. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.error(f"Failed to print oxygen bill. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            return False
        except Exception as e:
            logger.error(f"Connection error printing oxygen bill: {e}")
            return False

    def print_wound(self, wound_type, wound_number=None):
        """
        Generates and prints a wound card.
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

        # Determine wound number
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
        
        # Duplicate request logic to be strictly additive and safe
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.printer_url, data=data, headers={'Content-Type': 'application/json'})
            
            logger.info(f"Sending wound ({wound_type} {wound_number}) to printer...")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    logger.info(f"Successfully sent wound ({wound_type} {wound_number}) to printer.")
                    return True
                else:
                    logger.error(f"Failed to print wound. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.error(f"Failed to print wound. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            return False
        except Exception as e:
            logger.error(f"Connection error printing wound: {e}")
            return False

    def _print_entry(self, mission_id, entry_type):
        mission_data, file_path = self.mission_repo.find_mission_by_id(mission_id)
        
        if not mission_data:
            logger.error(f"Error: No mission file found for ID {mission_id}")
            return False

        return self._send_print_request(mission_data, file_path, entry_type)

    def _send_print_request(self, mission_data, file_path, entry_type):
        # Find the entry with the matching type
        entries = mission_data.get('entries', [])
        target_entry = None
        for entry in entries:
            if entry.get('type') == entry_type:
                target_entry = entry.get('data')
                break
        
        if not target_entry:
            logger.error(f"Error: No {entry_type} data found in {file_path}")
            return False

        # Construct the payload based on entry type
        if entry_type == "contract":
            payload = [
                "tmpl:tatourmi+mothership-contract",
                {
                    "id": "contract-template",
                    "name": "contract-template",
                    "data": target_entry
                },
                {}
            ]
        elif entry_type == "mission":
            payload = [
                "tmpl:tatourmi+mothership-mission",
                {
                    "id": "mission-template",
                    "name": "mission-template",
                    "data": target_entry
                },
                {}
            ]
        else:
            logger.error(f"Error: Unknown entry type {entry_type}")
            return False

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.printer_url, data=data, headers={'Content-Type': 'application/json'})
            
            logger.debug(f"Sending {entry_type} from {file_path} to printer...")
            logger.info(f"Sending {entry_type} to printer...")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    logger.debug(f"Successfully sent {entry_type} from {file_path} to printer.")
                    logger.info(f"Successfully sent {entry_type} to printer.")
                    return True
                else:
                    logger.debug(f"Failed to print {entry_type} from {file_path}. Status: {response.getcode()}")
                    logger.error(f"Failed to print {entry_type}. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.debug(f"Failed to print {entry_type} from {file_path}. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            logger.error(f"Failed to print {entry_type}. Status: {e.code}")
            return False
        except Exception as e:
            logger.error(f"Connection error printing {file_path}: {e}")
            return False

logger.info("Initializing Printer Service...")
try:
    printer_service = Printer()
    logger.info("Printer Service initialized.")
except Exception as e:
    logger.error("Failed to initialize Printer Service", exc_info=True)
    raise e
