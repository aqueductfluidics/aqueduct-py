"""SyringePump demo.

This demo program initializes a SyringePump device, sets 
the pump to run continuously at increasing flow rates,
and then reverses the direction of each pump input one by 
one as it reaches 0 flow rate. The program continuously
checks the flow rates of each pump input and sends new start 
commands to reverse the direction if the flow rate
reaches 0. 
"""
# import necessary modules
import time
from typing import List

from aqueduct.core.aq import Aqueduct, InitParams
from aqueduct.devices.pump.syringe import SyringePump, Status

# get initialization parameters
params = InitParams.parse()
# create an instance of the Aqueduct API with the given user_id, ip_address and port
aq = Aqueduct(params.user_id, params.ip_address, params.port)
# initialize the pump
aq.initialize(params.init)
# set a delay between sending commands to the pump
aq.set_command_delay(0.05)

# get the SyringePump device
pump: SyringePump = aq.devices.get("syringe_pump_000001")
# create a list to store the last direction used for each pump
last_directions: List[Status] = []

# create start commands for each pump at increasing rates
for i in range(0, pump.len):
    # create a command to set the pump to continuous mode, with a rate of i+1 ml/min, infusing
    c = pump.make_start_command(
        mode=pump.MODE.Continuous,
        rate_units=pump.RATE_UNITS.MlMin,
        rate_value=i + 1,
        direction=pump.STATUS.Infusing)
    # store the direction used for this command
    last_directions.append(pump.STATUS.Infusing)
    # set the command for this pump
    pump.set_command(pump.make_commands(), i, c)

# start the pumps
pump.start(pump.make_commands())

while True:
    # get the flow rates for each pump
    ul_min = pump.get_ul_min()
    # create a new list of commands for each pump
    commands = pump.make_commands()
    # check if any pumps have a flow rate of 0, and if so, reverse their direction
    for i, s in enumerate(ul_min):
        if ul_min[i] == 0:
            # reverse the direction of this pump
            d = last_directions[i].reverse()
            # create a new command with the reversed direction
            c = pump.make_start_command(
                mode=pump.MODE.Continuous,
                rate_units=pump.RATE_UNITS.MlMin,
                rate_value=i + 1,
                direction=d)
            # update the last direction used for this pump
            last_directions[i] = d
            # set the new command for this pump
            pump.set_command(commands, i, c)
    # start the pumps with the new commands
    pump.start(commands)
    # wait for a short time before checking again
    time.sleep(0.05)
