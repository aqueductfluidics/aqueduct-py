"""SolenoidValve demo.

This demo program initializes a SolenoidValve device and repeatedly toggles the position.
"""
import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.valve.solenoid import SolenoidValve

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

# get the SolenoidValve device
solenoid_valve: SolenoidValve = aq.devices.get("solenoid_valve_000001")

# continuously cycle through toggling the valve
while True:

    commands = solenoid_valve.make_commands()
    c = solenoid_valve.make_set_position_command(position=0)
    solenoid_valve.set_command(commands, 0, c)
    solenoid_valve.set_position(commands, record=True)
    print(solenoid_valve.get_position())

    time.sleep(2)

    commands = solenoid_valve.make_commands()
    c = solenoid_valve.make_set_position_command(position=1)
    solenoid_valve.set_command(commands, 0, c)
    solenoid_valve.set_position(commands, record=True)
    print(solenoid_valve.get_position())

    time.sleep(2)
