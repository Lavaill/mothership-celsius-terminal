import os

# --- DATA SOURCE CONFIGURATION ---
# This file contains the paths to all data sources used by the application.

# Base path for all data
DATA_PATH = "data"

# Mission paths
MISSIONS_ACTIVE_PATH = f"{DATA_PATH}/missions/active"
MISSIONS_INACTIVE_PATH = f"{DATA_PATH}/missions/inactive"

# Random generator paths
FORTUNES_PATH = f"{DATA_PATH}/random-generators/OxygenFortunes.json"
WOUNDS_PATH = f"{DATA_PATH}/random-generators/Wounds.json"

# --- USER CONFIGURATION (Uplink settings) ---
# We load from .env in the root if it exists, otherwise use defaults.
def load_env():
    config = {
        "VAULT_PATH": "C:/Workspace/Obsidian/Mothership",
        "CACHE_PATH": "logs/vault_cache"
    }
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip()
    return config

_config = load_env()
VAULT_PATH = _config["VAULT_PATH"]
CACHE_PATH = _config["CACHE_PATH"]
