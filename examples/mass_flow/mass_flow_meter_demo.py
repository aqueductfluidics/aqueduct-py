import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.core.units import MassFlowUnits
from aqueduct.devices.mass_flow import MassFlowMeter

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set the command delay for the Aqueduct instance
aq.set_command_delay(0.05)

# Get the mass flow meter device from the Aqueduct instance
mass_flow_meter: MassFlowMeter = aq.devices.get("mass_flow_meter_000001")

mass_flow_meter.set_sim_values((10.0,), MassFlowUnits.UL_MIN)
mass_flow_meter.set_sim_rates_of_change((0.5,), MassFlowUnits.UL_MIN)

# Continuously perform operations on the mass flow meter devices
while True:
    # Get and print the mass flow reading from the mass flow meter device
    print(f"Mass Flow: {mass_flow_meter.ul_min[0]:.3f}ul/min")

    # Pause for 5 seconds
    time.sleep(5)
