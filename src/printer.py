import urllib.request
import urllib.error
import json
import os
from src.jsonParser import JsonParser
from src.utils import logger

class Printer:
    def __init__(self):
        self.parser = JsonParser()
        self.printer_url = "http://127.0.0.1:7123/api/printTemplate"
        self.missions_path = "data/missions/active"

    def print_contract(self, mission_id):
        """
        Finds the json file containing the mission_id and sends it to the printer.
        """
        # We need to find the file that corresponds to the mission_id
        # The user input might be just the ID (e.g. BH-342) or part of the filename.
        # However, the prompt says "print contract {idOfTheMission}".
        # Let's look for a file that contains this ID in its name or content.
        # Based on the file list: BH-342_Zoomies.json, REPO-099_Boobytrap.json, AD-121_OperationAlDente.json
        # It seems the ID is the prefix of the filename.
        
        # Let's list all files in the directory
        # Since JsonParser is relative to resources, we can use os to list files in resources/data/missions/active
        # But JsonParser doesn't expose list_files.
        # We can use os.listdir on the full path.
        
        full_missions_path = os.path.join(self.parser.resources_dir, self.missions_path)
        
        if not os.path.exists(full_missions_path):
            logger.log(f"Error: Missions directory not found at {full_missions_path}")
            return False

        target_file = None
        for filename in os.listdir(full_missions_path):
            if mission_id in filename:
                target_file = filename
                break
        
        if not target_file:
            logger.log(f"Error: No mission file found for ID {mission_id}")
            return False

        return self._send_print_request(os.path.join(self.missions_path, target_file))

    def print_all_contracts(self):
        """
        Sends all contracts in the active missions folder to the printer.
        """
        full_missions_path = os.path.join(self.parser.resources_dir, self.missions_path)
        
        if not os.path.exists(full_missions_path):
            logger.log(f"Error: Missions directory not found at {full_missions_path}")
            return False

        success_count = 0
        files = [f for f in os.listdir(full_missions_path) if f.endswith('.json')]
        
        for filename in files:
            if self._send_print_request(os.path.join(self.missions_path, filename)):
                success_count += 1
        
        logger.log(f"Sent {success_count}/{len(files)} contracts to printer.")
        return success_count > 0

    def _send_print_request(self, relative_file_path):
        data = self.parser.read_json_file(relative_file_path)
        if not data:
            return False
            
        # The prompt says: "You should only send the first element of the Json to the body"
        # The example shows a list with 3 elements:
        # 1. "tmpl:tatourmi+mothership-contract"
        # 2. The data object (which seems to be the first element of the source JSON, wrapped)
        # 3. An empty object {}
        
        # The source JSON is a list of objects. The first object is the contract data.
        if isinstance(data, list) and len(data) > 0:
            contract_data = data[0]
        else:
            # Fallback if it's not a list or empty
            contract_data = data

        # Construct the payload as per the example
        payload = [
            "tmpl:tatourmi+mothership-contract",
            {
                "id": "contract-template",
                "name": "contract-template",
                "data": contract_data
            },
            {}
        ]

        try:
            json_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.printer_url, data=json_data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    logger.log(f"Successfully sent {relative_file_path} to printer.")
                    return True
                else:
                    logger.log(f"Failed to print {relative_file_path}. Status: {response.getcode()}")
                    return False
        except urllib.error.HTTPError as e:
            logger.log(f"Failed to print {relative_file_path}. Status: {e.code}, Response: {e.read().decode('utf-8')}")
            return False
        except Exception as e:
            logger.log(f"Connection error printing {relative_file_path}: {e}")
            return False

printer_service = Printer()
