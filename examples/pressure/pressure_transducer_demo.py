"""Pressure Transducer Example Script

This script demonstrates the usage of the `PressureTransducer` device from the 
Aqueduct library. It connects to an Aqueduct instance,
initializes the system, and performs operations on the pressure transducer device.
"""
import time

from aqueduct.core.aq import Aqueduct, InitParams
from aqueduct.devices.pressure import PressureTransducer

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set the command delay for the Aqueduct instance
aq.set_command_delay(0.05)

# Get the pressure transducer device from the Aqueduct instance
pressure_transducer: PressureTransducer = aq.devices.get("pressure_transducer_000001")

# Continuously perform operations on the pressure transducer device
while True:
    # Get and print the pressure reading from the pressure transducer device
    pressure_value = pressure_transducer.torr
    print(f"Pressure: {pressure_value}")

    # Pause for 5 seconds
    time.sleep(5)
