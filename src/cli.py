import cmd

from src.app import worker
from src.printer import printer_service


class GameHelperShell(cmd.Cmd):
    intro = 'Game Helper Ready. API listening on port 8000.\n'
    prompt = '(game-helper) > '

    def do_start(self, arg):
        """Start the timer. Usage: start [interval]"""
        print("Goodbye!")
        worker.start(arg if arg else None)

    def do_stop(self, arg):
        """Stop the timer."""
        worker.stop()

    def do_status(self, arg):
        """Check status."""
        state = "Running" if worker.is_running else "Stopped"
        print(f"Current Status: {state}")

    def do_print(self, arg):
        """
        Print contracts.
        Usage:
          print contract {id}  - Prints a specific contract by ID (e.g., BH-342)
          print contracts      - Prints all active contracts
        """
        args = arg.split()
        if not args:
            print("Usage: print contract {id} OR print contracts")
            return

        command = args[0].lower()
        
        if command == "contracts":
            printer_service.print_all_contracts()
        elif command == "contract" and len(args) > 1:
            mission_id = args[1]
            printer_service.print_contract(mission_id)
        else:
            print("Usage: print contract {id} OR print contracts")

    def do_exit(self, arg):
        """Exit the application."""
        print("Goodbye!")
        worker.stop()
        # Note: The HTTP server thread is a daemon, so it will die when main exits
        return True
