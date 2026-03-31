from mothership.services.printer_delivery import Printer

def test_printer_is_mocked():
    """
    This test verifies that the global safety lock is ACTIVE.
    It calls the 'send_to_hardware' method and checks that it was intercepted by a MagicMock.
    """
    printer = Printer()
    payload = {"test": "data"}
    
    # We call the method
    result = printer.send_to_hardware(payload, description="TEST LOCK")
    
    # Assertions
    assert result is True
    # If this is a real method, 'called_with' won't exist.
    # If it's a MagicMock, we can check its call history.
    assert printer.send_to_hardware.called is True
    assert printer.send_to_hardware.call_args[0][0] == payload
