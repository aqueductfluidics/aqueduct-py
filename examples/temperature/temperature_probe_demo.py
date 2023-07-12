import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.core.units import TemperatureUnits
from aqueduct.devices.temperature import TemperatureProbe

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set the command delay for the Aqueduct instance
aq.set_command_delay(0.05)

# Get the temperature probe device from the Aqueduct instance
temperature_probe: TemperatureProbe = aq.devices.get("temperature_probe_000001")

temperature_probe.set_sim_values((25.0,), TemperatureUnits.FAHRENHEIT)

temperature_probe.set_sim_rates_of_change((1.0,), TemperatureUnits.FAHRENHEIT)

# Continuously perform operations on the temperature probe device
while True:
    # Get and print the temperature reading from the temperature probe device
    print(f"Temperature: {temperature_probe.fahrenheit[0]:.3f}°F, {temperature_probe.celsius[0]:.3f}°C")

    # Pause for 5 seconds
    time.sleep(5)
