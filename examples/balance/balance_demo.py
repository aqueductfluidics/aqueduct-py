"""Balance Example Script

This script demonstrates the usage of the `Balance` device from the
Aqueduct library. It connects to an Aqueduct instance,
initializes the system, and performs operations on the balance device.
"""
import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.balance import Balance

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set the command delay for the Aqueduct instance
aq.set_command_delay(0.05)

# Get the balance device from the Aqueduct instance
balance: Balance = aq.devices.get("balance_000001")

# Continuously perform operations on the balance device
while True:
    # Set simulated rates of change for the balance device
    balance_rocs = [5]
    balance.set_sim_rates_of_change(balance_rocs)

    # Get and print the weight readings from the balance device in grams
    print(balance.grams)

    # Pause for 5 seconds
    time.sleep(5)

    # Get and print the weight readings again
    print(balance.grams)

    # Perform a tare operation on the balance device for the first input
    balance.tare(0)
