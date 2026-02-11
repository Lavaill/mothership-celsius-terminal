import cmd
import time
import threading
import traceback

from src.app import worker
from src.printer import printer_service
from src.interface import Interface
from src.utils import logger


class GameHelperShell(cmd.Cmd):
    intro = 'Game Helper Ready. API listening on port 8000.\n'
    prompt = Interface.ORANGE + '(game-helper) > ' + Interface.ENDC

    def preloop(self):
        """Hook that executes once when cmdloop() is called."""
        pass

    def default(self, line):
        """Handle unknown commands."""
        logger.log(f"Unknown command received: {line}")
        print(Interface.ORANGE + f"Unknown command: {line}" + Interface.ENDC)
        print(Interface.ORANGE + "Type 'help' for a list of commands." + Interface.ENDC)

    def onecmd(self, line):
        """Override onecmd to add logging and exception handling."""
        try:
            if line.strip():
                logger.log(f"Command executed: {line}")
            return super().onecmd(line)
        except Exception as e:
            logger.error(f"Crash during command execution: {line}", exc_info=True)
            print(Interface.FAIL + f"CRITICAL ERROR: {e}" + Interface.ENDC)
            print(Interface.FAIL + "Check logs for details." + Interface.ENDC)
            return False # Don't exit the shell on error

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
        
        if worker.is_running:
            progress = worker.progress
            circle = Interface.get_progress_circle(progress)
            # Create a progress bar
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            status_str = (
                f"STATUS:   {state}\n"
                f"INTERVAL: {worker.interval}m\n"
                f"NEXT:     {circle} [{bar}] {int(progress * 100)}%"
            )
        else:
            status_str = f"STATUS:   {state}\nINTERVAL: {worker.interval}m"
            
        Interface.draw_box(status_str, Interface.ORANGE)

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
        # args[0] is 'print'
        
        # If we are completing the first argument (subcommand)
        if len(args) == 1 or (len(args) == 2 and not line.endswith(' ')):
            options = ['contract', 'contracts', 'mission', 'oxygen']
            return [s for s in options if s.startswith(text)]
        
        # If we are completing the second argument (ID) for contract or mission
        if len(args) >= 2:
            subcommand = args[1].lower()
            if subcommand in ['contract', 'mission']:
                # Get available IDs
                ids = printer_service.get_available_mission_ids()
                # Filter by text if user started typing ID
                if len(args) == 3 and not line.endswith(' '):
                    return [s for s in ids if s.startswith(text)]
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
