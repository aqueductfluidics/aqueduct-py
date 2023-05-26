"""pH Probe Example Script

This script demonstrates the usage of the `PhProbe` device from the 
Aqueduct library. It connects to an Aqueduct instance,
initializes the system, and performs operations on the pH probe device.
"""
import time

from aqueduct.core.aq import Aqueduct, InitParams
from aqueduct.devices.ph import PhProbe

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set the command delay for the Aqueduct instance
aq.set_command_delay(0.05)

# Get the pH probe device from the Aqueduct instance
ph_probe: PhProbe = aq.devices.get("ph_probe_000001")

# Continuously perform operations on the pH probe device
while True:
    # Get and print the pH reading from the pH probe device
    ph_value = ph_probe.ph
    print(f"pH: {ph_value}")

    # Pause for 5 seconds
    time.sleep(5)
