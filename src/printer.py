import urllib.request
import urllib.error
import json
import os
import random
from src.jsonParser import JsonParser
from src.utils import logger

class Printer:
    def __init__(self):
        self.parser = JsonParser()
        self.printer_url = "http://127.0.0.1:7123/api/printTemplate"
        self.missions_path = "data/missions/active"
        self.fortunes_path = "data/random-generators/OxygenFortunes.json"

    def get_available_mission_ids(self):
        """
        Returns a list of all available mission IDs from the active missions folder.
        """
        full_missions_path = os.path.join(self.parser.resources_dir, self.missions_path)
        
        if not os.path.exists(full_missions_path):
            return []

        ids = []
        for filename in os.listdir(full_missions_path):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(self.missions_path, filename)
            data = self.parser.read_json_file(file_path)
            
            if data and data.get('id'):
                ids.append(data.get('id'))
        return ids

    def print_contract(self, mission_id):
        """
        Finds the json file containing the mission_id and sends the contract data to the printer.
        """
        return self._print_entry(mission_id, "contract")

    def print_mission(self, mission_id):
        """
        Finds the json file containing the mission_id and sends the mission data to the printer.
        """
        return self._print_entry(mission_id, "mission")

    def print_all_contracts(self):
        """
        Sends all contracts in the active missions folder to the printer.
        """
        return self._print_all_entries("contract")

    def print_oxygen_bill(self):
        """
        Sends an oxygen bill to the printer with a random quote.
        """
        fortunes = self.parser.read_json_file(self.fortunes_path)
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

    def _print_entry(self, mission_id, entry_type):
        full_missions_path = os.path.join(self.parser.resources_dir, self.missions_path)
        
        if not os.path.exists(full_missions_path):
            logger.error(f"Error: Missions directory not found at {full_missions_path}")
            return False

        # Iterate through all files to find the one with the matching ID
        target_file = None
        for filename in os.listdir(full_missions_path):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(self.missions_path, filename)
            data = self.parser.read_json_file(file_path)
            
            if data and data.get('id') == mission_id:
                target_file = file_path
                break
        
        if not target_file:
            logger.error(f"Error: No mission file found for ID {mission_id}")
            return False

        return self._send_print_request(target_file, entry_type)

    def _print_all_entries(self, entry_type):
        full_missions_path = os.path.join(self.parser.resources_dir, self.missions_path)
        
        if not os.path.exists(full_missions_path):
            logger.error(f"Error: Missions directory not found at {full_missions_path}")
            return False

        success_count = 0
        files = [f for f in os.listdir(full_missions_path) if f.endswith('.json')]
        
        for filename in files:
            if self._send_print_request(os.path.join(self.missions_path, filename), entry_type):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(files)} {entry_type}s to printer.")
        return success_count > 0

    def _send_print_request(self, relative_file_path, entry_type):
        data = self.parser.read_json_file(relative_file_path)
        if not data:
            return False
            
        # Find the entry with the matching type
        entries = data.get('entries', [])
        target_entry = None
        for entry in entries:
            if entry.get('type') == entry_type:
                target_entry = entry.get('data')
                break
        
        if not target_entry:
            logger.error(f"Error: No {entry_type} data found in {relative_file_path}")
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
            
            logger.debug(f"Sending {entry_type} from {relative_file_path} to printer...")
            logger.info(f"Sending {entry_type} to printer...")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    logger.debug(f"Successfully sent {entry_type} from {relative_file_path} to printer.")
                    logger.info(f"Successfully sent {entry_type} to printer.")
                    return True
                else:
                    logger.debug(f"Failed to print {entry_type} from {relative_file_path}. Status: {response.getcode()}")
                    logger.error(f"Failed to print {entry_type}. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.debug(f"Failed to print {entry_type} from {relative_file_path}. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            logger.error(f"Failed to print {entry_type}. Status: {e.code}")
            return False
        except Exception as e:
            logger.error(f"Connection error printing {relative_file_path}: {e}")
            return False

logger.info("Initializing Printer Service...")
try:
    printer_service = Printer()
    logger.info("Printer Service initialized.")
except Exception as e:
    logger.error("Failed to initialize Printer Service", exc_info=True)
    raise e
