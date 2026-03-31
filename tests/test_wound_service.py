from mothership.services.wound_service import WoundService
from mothership.data.repository import GeneratorRepository
from unittest.mock import MagicMock

def test_wound_service_payload_structure():
    """
    Verifies that the WoundService generates the correct JSON payload 
    format for the printer without actually printing.
    """
    # Mock Repository to return consistent data
    mock_repo = MagicMock(spec=GeneratorRepository)
    mock_repo.get_wounds_data.return_value = {
        "wound-severity": {"1": "Scratch"},
        "wound-tables": [{"type": "bleeding", "1": "Blood everywhere"}]
    }
    
    service = WoundService(generator_repo=mock_repo)
    
    # Trigger a wound print
    service.print_wound("bleeding", wound_number=1)
    
    # Verify the printer was called with the correct payload structure
    from mothership.services.printer_delivery import printer_io
    
    assert printer_io.send_to_hardware.called
    payload = printer_io.send_to_hardware.call_args[0][0]
    
    # Check payload structure matches our templates
    assert payload[0] == "tmpl:tatourmi+mothership-wound"
    assert payload[1]["data"]["severity"] == "Scratch"
    assert payload[1]["data"]["type"] == "BLEEDING"
    assert payload[1]["data"]["desc"] == "Blood everywhere"
