from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

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
            success = worker.start(interval)
            response_msg = "Timer started" if success else "Timer already running"

        elif parsed.path == '/stop':
            success = worker.stop()
            response_msg = "Timer stopped" if success else "Timer not running"

        elif parsed.path == '/status':
            state = "Running" if worker.is_running else "Stopped"
            response_msg = f"Status: {state} | Interval: {worker.interval}"
            
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
