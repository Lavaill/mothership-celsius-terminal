import cmd
import sys
try:
    import readline
    # Fix for Python 3.13 + pyreadline3 compatibility
    if readline and not hasattr(readline, 'backend'):
        readline.backend = 'readline'
except ImportError:
    readline = None
    # This is common on Windows without pyreadline3 installed
    if sys.platform == 'win32':
        print("\n[!] Warning: 'readline' not found. Tab-completion will be disabled.")
        print("[!] Run 'pip install pyreadline3' to enable it.\n")

from src.app import worker
from src.printer import printer_service
from src.interface import Interface


class GameHelperShell(cmd.Cmd):
    intro = 'Game Helper Ready. API listening on port 8000.\n'
    prompt = Interface.ORANGE + 'mothership-helper > ' + Interface.ORANGE

    def do_start(self, arg):
        """Start the timer. Usage: start [interval_in_minutes] [api_url]"""
        args = arg.split()
        interval = args[0] if len(args) > 0 else None
        api_url = args[1] if len(args) > 1 else None
        
        print(Interface.ORANGE + "Starting timer..." + Interface.ENDC)
        worker.start(interval, api_url)

    def do_stop(self, arg):
        """Stop the timer."""
        worker.stop()

    def do_status(self, arg):
        """Check status."""
        state = "Running" if worker.is_running else "Stopped"
        print(Interface.ORANGE + f"Current Status: {state} | Interval: {worker.interval}m" + Interface.ENDC)

    def do_print(self, arg):
        """
        Print contracts, missions, or oxygen bill.
        Usage:
          print contract {id}  - Prints a specific contract by ID (e.g., BH-342)
          print contracts      - Prints all active contracts
          print mission {id}   - Prints a specific mission by ID (e.g., BH-342)
          print oxygen         - Prints an oxygen bill
        """
        args = arg.split()
        if not args:
            print(Interface.ORANGE + "Usage: print contract {id} OR print contracts OR print mission {id} OR print oxygen" + Interface.ENDC)
            return

        command = args[0].lower()
        
        if command == "contracts":
            printer_service.print_all_contracts()
        elif command == "contract" and len(args) > 1:
            mission_id = args[1]
            printer_service.print_contract(mission_id)
        elif command == "mission" and len(args) > 1:
            mission_id = args[1]
            printer_service.print_mission(mission_id)
        elif command == "oxygen":
            printer_service.print_oxygen_bill()
        else:
            print(Interface.ORANGE + "Usage: print contract {id} OR print contracts OR print mission {id} OR print oxygen" + Interface.ENDC)

    def complete_print(self, text, line, begidx, endidx):
        """Autocomplete for print command"""
        args = line.split()
        text_lower = text.lower()
        # args[0] is 'print'
        
        # If we are completing the first argument (subcommand)
        if len(args) == 1 or (len(args) == 2 and not line.endswith(' ')):
            options = ['contract', 'contracts', 'mission', 'oxygen']
            return [s for s in options if s.startswith(text_lower)]
        
        # If we are completing the second argument (ID) for contract or mission
        if len(args) >= 2:
            subcommand = args[1].lower()
            if subcommand in ['contract', 'mission']:
                # Get available IDs
                ids = printer_service.get_available_mission_ids()
                # Filter by text if user started typing ID
                if len(args) == 3 and not line.endswith(' '):
                    return [s for s in ids if s.lower().startswith(text_lower)]
                # If user just typed 'print contract ', show all IDs
                elif len(args) == 2 and line.endswith(' '):
                    return ids
                    
        return []

    def do_exit(self, arg):
        """Exit the application."""
        print(Interface.ORANGE + "Goodbye!" + Interface.ENDC)
        worker.stop()
        # Note: The HTTP server thread is a daemon, so it will die when main exits
        return True

    def preloop(self):
        if readline:
            readline.parse_and_bind('set completion-ignore-case on')
            if hasattr(readline, 'set_completion_display_matches_hook'):
                readline.set_completion_display_matches_hook(self.completion_display_hook)

    def completion_display_hook(self, substitution, matches, longest_match_length):
        print()
        sys.stdout.write(Interface.WHITE)
        self.columnize(matches)
        sys.stdout.write(Interface.ORANGE)
        sys.stdout.flush()
