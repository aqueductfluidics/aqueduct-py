"""PinchValve demo.

This demo program initializes a PinchValve device, sets it to gradually open and close 
over a range of values from 0 to 100 and back down to 0. The program continuously 
checks the position of the valve and sends new position commands to gradually change 
the valve's position. The time delay between position changes is decreased from 
0.1 seconds to 0.001 seconds in increments of 10x to create a more gradual transition. 
During each loop, the current position of the valve is printed to the console.
"""
import time

from aqueduct.core.aq import Aqueduct, InitParams
from aqueduct.devices.valve.pinch import PinchValve

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

# get the PinchValve device
pinch_valve: PinchValve = aq.devices.get("PV000001")

# continuously cycle through opening and closing the valve
while True:

    # loop through various sleep times to change the speed of valve movement
    for sleep in (0.001, 0.01, 0.1):

        # loop through the valve position values from 0 to 100 percent open
        for i in range(0, 100):
            commands = pinch_valve.make_commands()
            c = pinch_valve.make_set_poisition_command(pct_open=i / 100.)
            pinch_valve.set_command(commands, 0, c)
            pinch_valve.set_position(commands, record=True)
            print(pinch_valve.get_pct_open())
            time.sleep(sleep)

        # loop through the valve position values from 100 to 0 percent open
        for i in range(100, 0, -1):
            commands = pinch_valve.make_commands()
            c = pinch_valve.make_set_poisition_command(pct_open=i / 100.)
            pinch_valve.set_command(commands, 0, c)
            pinch_valve.set_position(commands, record=True)
            print(pinch_valve.get_pct_open())
            time.sleep(sleep)
