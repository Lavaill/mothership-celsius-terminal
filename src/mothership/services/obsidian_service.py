import os
import json
from mothership.data.repository import VaultRepository
from mothership.core.config import CACHE_PATH
from mothership.core.utils import logger

class ObsidianService:
    """
    Parses Markdown files from Obsidian into our internal JSON structure.
    Maintains an in-memory registry for speed and a physical cache for debugging.
    """
    def __init__(self, vault_repo=None):
        self.vault_repo = vault_repo or VaultRepository()
        self.cache_path = CACHE_PATH
        self.registry = {} # In-memory: {mission_id: mission_data}
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def sync_vault(self):
        """
        Scans the vault, parses files, and populates the registry.
        Writes 'Shadow JSONs' to the cache folder for debugging.
        """
        logger.info("Initializing Vault Uplink Sync...")
        md_files = self.vault_repo.get_markdown_files()
        
        for file_path in md_files:
            # Barebones logic for now
            # 1. Read MD
            # 2. Parse (Logic to be implemented)
            # 3. Add to self.registry
            # 4. Save to CACHE_PATH as .json
            pass
        
        logger.info(f"Sync complete. Indexed {len(self.registry)} entries from Vault.")

    def get_mission_data(self, mission_id):
        """
        Retrieves mission data from the in-memory registry.
        """
        return self.registry.get(mission_id)
