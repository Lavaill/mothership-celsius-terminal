import threading
from src.server import run_server
from src.cli import GameHelperShell

if __name__ == '__main__':
    # Start the API Server in a separate thread
    api_thread = threading.Thread(target=run_server, args=(8000,), daemon=True)
    api_thread.start()

    # Start the CLI in the main thread
    try:
        GameHelperShell().cmdloop()
    except KeyboardInterrupt:
        print("\nForce closing...")