import json
import os

class JsonParser:
    def __init__(self, project_root=None):
        if project_root is None:
            # Current file: src/mothership/data/json_parser.py
            # 1. data/
            # 2. mothership/
            # 3. src/
            # 4. MothershipCli/ (Root)
            data_dir = os.path.dirname(os.path.abspath(__file__))
            mothership_dir = os.path.dirname(data_dir)
            src_dir = os.path.dirname(mothership_dir)
            project_root = os.path.dirname(src_dir)
        
        self.resources_dir = os.path.join(project_root, 'resources')

    def read_json_file(self, relative_path):
        """
        Reads a .json file from the resources directory.
        
        Args:
            relative_path (str): The path to the json file relative to the resources folder.
                                 Example: 'subfolder/data.json'
        
        Returns:
            dict: The content of the json file, or None if an error occurs.
        """
        file_path = os.path.join(self.resources_dir, relative_path)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
