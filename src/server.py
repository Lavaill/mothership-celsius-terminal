from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import signal

from src.app import worker
from src.utils import logger
from src.printer import printer_service

class GameRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL: /start?interval=10
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        response_msg = "OK"
        status_code = 200

        if parsed.path == '/start':
            interval = params.get('interval', [None])[0]
            api_url = params.get('api_url', [None])[0]
            success = worker.start(interval, api_url)
            response_msg = "Timer started" if success else "Timer already running"

        elif parsed.path == '/stop':
            success = worker.stop()
            response_msg = "Timer stopped" if success else "Timer not running"

        elif parsed.path == '/status':
            state = "Running" if worker.is_running else "Stopped"
            # Return JSON for status to be more useful for API consumers
            status_data = {
                "state": state,
                "interval": worker.interval,
                "progress": round(worker.progress, 2)
            }
            response_msg = json.dumps(status_data)
            self.send_header('Content-type', 'application/json')

        elif parsed.path == '/exit':
            response_msg = "Shutting down system..."
            # We need to send the response before killing the process
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_msg.encode())
            
            # Shutdown logic
            worker.stop()
            logger.info("System exit requested via API.")
            # Send SIGINT to the main process to trigger a clean exit
            os.kill(os.getpid(), signal.SIGINT)
            return

        elif parsed.path == '/print/contracts':
            # API endpoint to print all contracts
            # Example: GET /print/contracts
            success = printer_service.print_all_contracts()
            response_msg = "Printing all contracts initiated" if success else "Failed to initiate printing"
            
        elif parsed.path.startswith('/print/contract/'):
            # API endpoint to print a specific contract
            # Example: GET /print/contract/BH-342
            mission_id = parsed.path.split('/')[-1]
            if mission_id:
                success = printer_service.print_contract(mission_id)
                response_msg = f"Printing contract {mission_id} initiated" if success else f"Failed to find or print contract {mission_id}"
            else:
                status_code = 400
                response_msg = "Missing mission ID"

        elif parsed.path.startswith('/print/mission/'):
            # API endpoint to print a specific mission
            # Example: GET /print/mission/BH-342
            mission_id = parsed.path.split('/')[-1]
            if mission_id:
                success = printer_service.print_mission(mission_id)
                response_msg = f"Printing mission {mission_id} initiated" if success else f"Failed to find or print mission {mission_id}"
            else:
                status_code = 400
                response_msg = "Missing mission ID"

        elif parsed.path == '/print/oxygen':
            # API endpoint to print an oxygen bill
            # Example: GET /print/oxygen
            success = printer_service.print_oxygen_bill()
            response_msg = "Printing oxygen bill initiated" if success else "Failed to initiate printing"

        elif parsed.path.startswith('/print/wound/'):
            # API endpoint to print a wound
            # Example: GET /print/wound/BLEEDING?number=5
            wound_type = parsed.path.split('/')[-1]
            wound_number = params.get('number', [None])[0]
            
            if wound_type:
                success = printer_service.print_wound(wound_type, wound_number)
                response_msg = f"Printing wound {wound_type} initiated" if success else f"Failed to print wound {wound_type}"
            else:
                status_code = 400
                response_msg = "Missing wound type"

        else:
            status_code = 404
            response_msg = "Unknown command"

        # Send Response
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_msg.encode())

    # Silence the default HTTP access logs to keep console clean
    def log_message(self, format, *args):
        pass


def run_server(port=8000):
    server = HTTPServer(('localhost', port), GameRequestHandler)
    logger.log(f"API Server listening on http://localhost:{port}")
    server.serve_forever()
