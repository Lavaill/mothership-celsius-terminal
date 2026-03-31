import os
from mothership.core.utils import logger
from mothership.data.json_parser import JsonParser
from mothership.core.config import MISSIONS_ACTIVE_PATH, MISSIONS_INACTIVE_PATH, WOUNDS_PATH, FORTUNES_PATH, VAULT_PATH

class VaultRepository:
    """
    Handles discovery and reading of Markdown files from an external Obsidian Vault.
    Supports absolute paths and identifies 'Printable' notes.
    """
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or VAULT_PATH

    def get_markdown_files(self):
        """
        Returns a list of all .md files in the vault (recursive).
        """
        if not os.path.exists(self.vault_path):
            logger.error(f"Vault path not found: {self.vault_path}")
            return []
        
        md_files = []
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
        return md_files

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
