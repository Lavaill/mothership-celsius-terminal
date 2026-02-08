import sys
import time
import os
import colorama

class Interface:
    # Initialize colorama to ensure ANSI codes work on Windows
    colorama.init()

    # Retro Terminal Colors (Mapped to Colorama for Windows compatibility)
    HEADER = colorama.Fore.MAGENTA
    BLUE = colorama.Fore.BLUE
    CYAN = colorama.Fore.CYAN
    GREEN = colorama.Fore.GREEN
    # Using Bright Yellow to simulate Amber/Orange on standard terminals
    ORANGE = colorama.Fore.YELLOW + colorama.Style.BRIGHT
    WHITE = colorama.Fore.WHITE + colorama.Style.BRIGHT
    WARNING = colorama.Fore.YELLOW
    FAIL = colorama.Fore.RED
    ENDC = colorama.Style.RESET_ALL
    BOLD = colorama.Style.BRIGHT
    UNDERLINE = ''

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
        print(Interface.ORANGE + Interface.LOGO + Interface.ENDC)
        Interface.type_text("INITIALIZING MOTHERSHIP UPLINK...", Interface.STARTUP_DELAY, Interface.ORANGE)
        time.sleep(Interface.LINE_SLEEP)
        Interface.type_text("CONNECTION ESTABLISHED.", Interface.STARTUP_DELAY, Interface.ORANGE)
        print(Interface.ORANGE + "-" * 60 + Interface.ENDC)

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