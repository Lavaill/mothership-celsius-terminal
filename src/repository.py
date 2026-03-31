import os
from src.utils import logger
from src.jsonParser import JsonParser
from src.config import MISSIONS_ACTIVE_PATH, MISSIONS_INACTIVE_PATH, WOUNDS_PATH, FORTUNES_PATH

class MissionRepository:
    def __init__(self):
        self.parser = JsonParser()

    def get_all_mission_ids(self):
        """
        Returns a list of all available mission IDs from all mission folders.
        """
        ids = []
        
        def scan_dir(relative_path):
            full_path = os.path.join(self.parser.resources_dir, relative_path)
            if not os.path.exists(full_path):
                return
            
            for filename in os.listdir(full_path):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(relative_path, filename)
                data = self.parser.read_json_file(file_path)
                
                if data and data.get('id'):
                    ids.append(data.get('id'))

        scan_dir(MISSIONS_ACTIVE_PATH)
        scan_dir(MISSIONS_INACTIVE_PATH)
        
        return ids

    def find_mission_by_id(self, mission_id):
        """
        Finds a mission by its ID in any of the mission folders.
        """
        search_paths = [MISSIONS_ACTIVE_PATH, MISSIONS_INACTIVE_PATH]
        
        for base_path in search_paths:
            full_path = os.path.join(self.parser.resources_dir, base_path)
            if not os.path.exists(full_path):
                continue
                
            for filename in os.listdir(full_path):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(base_path, filename)
                data = self.parser.read_json_file(file_path)
                
                if data and data.get('id') == mission_id:
                    return data, file_path
        
        return None, None

    def get_active_missions(self):
        """
        Returns a list of all missions in the active folder.
        """
        missions = []
        full_path = os.path.join(self.parser.resources_dir, MISSIONS_ACTIVE_PATH)
        if not os.path.exists(full_path):
            return missions
            
        for filename in os.listdir(full_path):
            logger.info(filename)
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(MISSIONS_ACTIVE_PATH, filename)
            data = self.parser.read_json_file(file_path)
            if data:
                missions.append((data, file_path))
                
        return missions

class GeneratorRepository:
    def __init__(self):
        self.parser = JsonParser()

    def get_wounds_data(self):
        """Reads and returns the entire wounds data structure."""
        return self.parser.read_json_file(WOUNDS_PATH)

    def get_fortunes_data(self):
        """Reads and returns the list of oxygen fortunes."""
        return self.parser.read_json_file(FORTUNES_PATH)
