from mothership.data.repository import MissionRepository
from mothership.core.utils import logger
from mothership.services.printer_delivery import printer_io

class MissionService:
    """
    Handles all logic related to mission data retrieval and contract printing.
    """
    def __init__(self, mission_repo=None):
        self.mission_repo = mission_repo or MissionRepository()

    def get_mission_ids(self):
        """
        Returns a list of all mission IDs (for TUI autocomplete).
        """
        return self.mission_repo.get_all_mission_ids()

    def print_contract(self, mission_id):
        """
        Retrieves contract data and sends to hardware.
        """
        return self._prepare_and_send(mission_id, "contract")

    def print_mission(self, mission_id):
        """
        Retrieves mission data and sends to hardware.
        """
        return self._prepare_and_send(mission_id, "mission")

    def print_all_contracts(self):
        """
        Prints all active contracts.
        """
        active_missions = self.mission_repo.get_active_missions()
        success_count = 0
        for mission_data, file_path in active_missions:
            if self._send_payload(mission_data, file_path, "contract"):
                success_count += 1
        
        logger.info(f"Processed {success_count}/{len(active_missions)} contracts.")
        return success_count > 0

    def _prepare_and_send(self, mission_id, entry_type):
        mission_data, file_path = self.mission_repo.find_mission_by_id(mission_id)
        if not mission_data:
            logger.error(f"Error: Mission {mission_id} not found.")
            return False
        return self._send_payload(mission_data, file_path, entry_type)

    def _send_payload(self, mission_data, file_path, entry_type):
        entries = mission_data.get('entries', [])
        target_entry = next((e.get('data') for e in entries if e.get('type') == entry_type), None)
        
        if not target_entry:
            logger.error(f"Error: No {entry_type} data in {file_path}")
            return False

        template_map = {
            "contract": "tmpl:tatourmi+mothership-contract",
            "mission": "tmpl:tatourmi+mothership-mission"
        }

        payload = [
            template_map.get(entry_type, "unknown-template"),
            {
                "id": f"{entry_type}-template",
                "name": f"{entry_type}-template",
                "data": target_entry
            },
            {}
        ]

        return printer_io.send_to_hardware(payload, description=f"{entry_type} for {file_path}")
