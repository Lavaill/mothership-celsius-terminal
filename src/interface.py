import sys
import time
import os

class Interface:
    # Retro Terminal Colors
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    ORANGE = '\033[38;5;208m'  # Dark Orange (ANSI 256 color)
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Constants for timing
    TYPE_DELAY = 0.02
    STARTUP_DELAY = 0.04
    LINE_SLEEP = 0.5

    LOGO = r"""
  __  __  ___ _____ _   _ _____ ____  ____  _   _ ___ ____  
 |  \/  |/ _ \_   _| | | | ____|  _ \/ ___|| | | |_ _|  _ \ 
 | |\/| | | | || | | |_| |  _| | |_) \___ \| |_| || || |_) |
 | |  | | |_| || | |  _  | |___|  _ < ___) |  _  || ||  __/ 
 |_|  |_|\___/ |_| |_| |_|_____|_| \_\____/|_| |_|___|_|    
    """

    @staticmethod
    def startup():
        Interface.clear()
        
        # New Header Design
        print(Interface.ORANGE + "=" * 60 + Interface.ENDC)
        print(Interface.ORANGE + "||" + " " * 56 + "||" + Interface.ENDC)
        print(Interface.ORANGE + "||" + "MOTHERSHIP UPLINK TERMINAL".center(56) + "||" + Interface.ENDC)
        print(Interface.ORANGE + "||" + " " * 56 + "||" + Interface.ENDC)
        print(Interface.ORANGE + "=" * 60 + Interface.ENDC)
        print()
        
        print(Interface.ORANGE + Interface.LOGO + Interface.ENDC)
        print()
        
        Interface.draw_box("INITIALIZING SYSTEM...", Interface.ORANGE)
        time.sleep(Interface.LINE_SLEEP)
        
        Interface.type_text("ESTABLISHING SECURE CONNECTION...", Interface.STARTUP_DELAY, Interface.ORANGE)
        time.sleep(0.2)
        Interface.type_text("VERIFYING CREDENTIALS...", Interface.STARTUP_DELAY, Interface.ORANGE)
        time.sleep(0.2)
        Interface.type_text("ACCESS GRANTED.", Interface.STARTUP_DELAY, Interface.ORANGE)

        print(Interface.ORANGE + "+" + "=" * 60 + "+" + Interface.ENDC)

    @staticmethod
    def type_text(text, delay=TYPE_DELAY, color=None):
        if color:
            sys.stdout.write(color)
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        if color:
            sys.stdout.write(Interface.ENDC)
        print()

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def draw_box(text, color=None):
        """Draws a box with sharp corners and double lines."""
        lines = text.split('\n')
        width = max(len(line) for line in lines) + 2
        
        c_start = color if color else ""
        c_end = Interface.ENDC if color else ""

        # Top
        print(f"{c_start}╔{'═' * width}╗{c_end}")
        
        # Content
        for line in lines:
            padding = width - len(line) - 1
            print(f"{c_start}║ {line}{' ' * padding}║{c_end}")
            
        # Bottom
        print(f"{c_start}╚{'═' * width}╝{c_end}")

    @staticmethod
    def get_progress_circle(percent):
        """Returns an ASCII character representing progress (0.0 to 1.0)."""
        # Clamp percent
        p = max(0.0, min(1.0, percent))
        
        if p < 0.2: return "[ ]"
        elif p < 0.4: return "[.]"
        elif p < 0.6: return "[o]"
        elif p < 0.8: return "[O]"
        else: return "[@]"
