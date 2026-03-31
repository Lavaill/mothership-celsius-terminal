# --- THEME CONFIGURATION ---
# This file contains all aesthetic elements for the Mothership CLI.
# DO NOT MODIFY without explicit instruction.

# --- TIMING CONSTANTS ---
TYPE_DELAY = 0.01
LINE_DELAY = 0.2

# --- THEMES ---
THEMES = {
    "mothership": {
        "primary": "#FF9500",
        "secondary": "#8A5200",
        "header": "MOTHERSHIP // TERMINAL ZERO",
        "logo": """
   __  __ 
  |  \/  |
  | |\/| |
  |_|  |_|
""",
        "startup": [
            "Initializing Kernel...",
            "Loading Modules: [OXYGEN BILLING, WOUNDS EVALUATION, LEDGERS, CONTRACT]... OK",
            "Mounting File System... OK",
            "Opening Air-Locked Connections... SUCCESS",
            "Establishing Printer Status... SUCCESS",
            "Welcome, Administrator."
        ]
    },
    "prospero": {
        "primary": "#FF1493",
        "secondary": "#8B0A50",
        "header": "PROSPERO'S DREAM // OUTPOST ADMINISTRATION",
        "logo": """
   ___ 
  | _ \\
  |  _/
  |_|  
    """,
        "startup": [
            "Bypassing Security Protocols...",
            "Spoofing ID Signature... [PROSPERO_GUEST]",
            "Connecting to Life-Support systems... SUCCESS",
            "WARNING: UNSUPERVISED CONNECTIONS DETECTED",
            "Welcome to the Station, Yandee."
        ]
    },
    "helios": {
        "primary": "#FFFFFF",
        "secondary": "#808080",
        "header": "HELIOS CORPORATION // BIOMETRIC LINK",
        "logo": """
   _  _ 
  | || |
  | __ |
  |_||_|
    """,
        "startup": [
            "Scanning Biometrics...",
            "Heart Rate: 72 BPM. Stress Level: 12%.",
            "Authenticating Employee ID...",
            "Access Granted: Level 4 Clearance.",
            "Helios Health: We Care Because You Pay."
        ]
    },
    "astra": {
        "primary": "#33FF00",
        "secondary": "#1A8000",
        "header": "ASTRA HEAVY IND // FACTORY GATE",
        "logo": """
    __  
   /  \\ 
  | /\\ |
  |_||_|
    """,
        "startup": [
            "Booting Industrial Controller...",
            "Checking Safety Interlocks... DISABLED",
            "Connecting to Factory Floor...",
            "Production Efficiency: 94%.",
            "Astra Heavy Industries: Building Tomorrow."
        ]
    },
    "parallax": {
        "primary": "#9D00FF",
        "secondary": "#4B0082",
        "header": "PARALLAX SYSTEMS // FTL NODE",
        "logo": """
   ___ 
  | _ \\
  |  _/
  |_|  
    """,
        "startup": [
            "Aligning Phase Arrays...",
            "Calculating Jump Coordinates...",
            "Syncing with FTL Beacon...",
            "Reality Anchor: STABLE.",
            "Parallax Systems: Everywhere at Once."
        ]
    }
}
