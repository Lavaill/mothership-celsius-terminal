from .wound_service import WoundService
from .mission_service import MissionService
from .billing_service import BillingService
from .obsidian_service import ObsidianService
from mothership.core.app import timer_manager

class MothershipService:
    """
    Facade providing a unified interface to all backend services.
    Acts as the single point of contact for the TUI and API server.
    """
    def __init__(self):
        self.wounds = WoundService()
        self.missions = MissionService()
        self.billing = BillingService()
        self.obsidian = ObsidianService()

        # Initialize named Timer Worker
        oxygen_worker = timer_manager.register("oxygen-timer", interval=20)
        oxygen_worker.set_task(self.print_oxygen_bill)

    # --- Discovery Methods (for Autocomplete) ---
    def get_available_mission_ids(self):
        # Combine local mission IDs and Obsidian mission IDs
        local_ids = self.missions.get_mission_ids()
        vault_ids = list(self.obsidian.registry.keys())
        return list(set(local_ids + vault_ids))

    def get_wound_types(self):
        return self.wounds.get_wound_types()

    def get_timer_names(self):
        return timer_manager.list_names()

    def sync_vault(self):
        """Uplink sync with external Obsidian Vault."""
        return self.obsidian.sync_vault()

    # --- Printing Methods ---
    def print_contract(self, mission_id):
        return self.missions.print_contract(mission_id)

    def print_mission(self, mission_id):
        return self.missions.print_mission(mission_id)

    def print_all_contracts(self):
        return self.missions.print_all_contracts()

    def print_oxygen_bill(self):
        return self.billing.print_oxygen_bill()

    def print_wound(self, wound_type, wound_number=None):
        return self.wounds.print_wound(wound_type, wound_number)

# Global instance for the application
mothership_service = MothershipService()
