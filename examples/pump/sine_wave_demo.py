"""Demomstrate changing the rates of three pumps using a sine wave generator."""
import math

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.pump import PeristalticPump

# parse initialization parameters and create Aqueduct instance
params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# initialize the devices and set a command delay
aq.initialize(params.init)
aq.set_command_delay(0.05)

# get the peristaltic pump device and create a command object
pump1: PeristalticPump = aq.devices.get("peristaltic_pump_000001")

# get the peristaltic pump device and create a command object
pump2: PeristalticPump = aq.devices.get("peristaltic_pump_000002")

# get the peristaltic pump device and create a command object
pump3: PeristalticPump = aq.devices.get("peristaltic_pump_000003")

MEAN = 5

commands = pump1.make_commands()
c = pump1.make_start_command(
    mode=pump1.MODE.Continuous,
    rate_units=pump1.RATE_UNITS.MlMin,
    rate_value=MEAN,
    direction=pump1.STATUS.Clockwise,
)

# set the command for each channel and start the pump
for i in range(0, pump1.len):
    pump1.set_command(commands, i, c)

pump1.start(commands)
pump2.start(commands)
pump3.start(commands)

STEPS = 100


def get_delta(step: int, phase: float) -> float:
    """
    Calculate the delta value based on step and phase.

    :param step: The current step.
    :type step: int
    :param phase: The phase value.
    :type phase: float
    :return: The calculated delta value.
    :rtype: float
    """
    return math.sin(step / STEPS * (2 * math.pi) + phase)


def change_speed(pump: PeristalticPump, rate_value: float):
    """
    Change the speed of a peristaltic pump.

    :param pump: The PeristalticPump instance.
    :type pump: PeristalticPump
    :param rate_value: The new rate value.
    :type rate_value: float
    """

    # create a command to change the pump speed
    c = pump.make_change_speed_command(
        rate_value=rate_value, rate_units=pump1.RATE_UNITS.MlMin
    )

    # set the command for each channel and change the pump speed
    for i in range(0, pump.len):
        pump.set_command(commands, i, c)

    pump.change_speed(commands)


# loop
while True:

    for i in range(0, STEPS):
        pump1_delta = get_delta(i, 0)
        pump2_delta = get_delta(i, 2 * math.pi / 3)
        pump3_delta = get_delta(i, 4 * math.pi / 3)

        change_speed(pump1, MEAN + pump1_delta)
        change_speed(pump2, MEAN + pump2_delta)
        change_speed(pump3, MEAN + pump3_delta)
