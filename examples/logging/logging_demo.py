"""A module for demonstrating logging in the Aqueduct framework.

This demo program demonstrates setting the log file name and then
logging a series of messages at different `levels`.
"""
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams

# parse initialization parameters and create Aqueduct instance
params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# optionally set the log file name
aq.set_log_file_name("new_log_file")

# initialize the devices and set a command delay
aq.initialize(params.init)
aq.set_command_delay(0.05)

aq.debug("debug message!")
aq.info("info message!")
aq.warning("warning message!")
aq.error("error message!")
aq.critical("critical message!")
