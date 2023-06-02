"""A module for controlling peristaltic pumps using the Aqueduct framework.

This demo program initializes a PeristalticPump device, sets the pump to run
continuously at a specific flow rate, and then reverses the direction of the
pump's rotation after a certain amount of time has passed. The program continuously
checks the flow rate of the pump and sends new start commands to reverse
the direction if the flow rate reaches 0.
"""
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams

# parse initialization parameters and create Aqueduct instance
params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# initialize the devices and set a command delay
aq.initialize(params.init)
aq.set_command_delay(0.05)

aq.debug("debug message!")
aq.info("info message!")
aq.warning("warning message!")
aq.error("error message!")
aq.critical("critical message!")
