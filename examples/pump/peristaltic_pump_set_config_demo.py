"""A module for controlling peristaltic pumps using the Aqueduct framework.

This demo program initializes a PeristalticPump device, sets the pump to run
continuously at a specific flow rate, and then reverses the direction of the
pump's rotation after a certain amount of time has passed. The program continuously
checks the flow rate of the pump and sends new start commands to reverse
the direction if the flow rate reaches 0.
"""
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.pump import PeristalticPump
from aqueduct.devices.pump.peristaltic.types.aqueduct import StepperMotorConfig

# parse initialization parameters and create Aqueduct instance
params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# initialize the devices and set a command delay
aq.initialize(params.init)
aq.set_command_delay(0.05)

# get the peristaltic pump device and create a command object
pump: PeristalticPump = aq.devices.get("peristaltic_pump_000001")

# change the rev_per_ml of the first motor
# setting `steps_per_rev` to `None` means the value will be unchanged
config = StepperMotorConfig(rev_per_ml=42, steps_per_rev=None)

pump.set_config([config])
