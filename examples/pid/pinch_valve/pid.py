"""
Demonstration of setting up a PID controller with Aqueduct devices.
"""

# Import necessary modules
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.core.pid import Pid, Schedule, Controller, ControllerSchedule
from aqueduct.devices.valve.pinch import PinchValve
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.pressure.transducer import PressureTransducer

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set a delay between sending commands to the pump
aq.set_command_delay(0.05)

# Define names for devices
PUMP_NAME = "PP"
XDCR_NAME = "TDCR"
PV_NAME = "PV"

# Retrieve the setup to confirm the added devices
aq.get_setup()

# Retrieve device instances
pp: PeristalticPump = aq.devices.get(PUMP_NAME)
tdcr: PressureTransducer = aq.devices.get(XDCR_NAME)
pv: PinchValve = aq.devices.get(PV_NAME)

# Define PID controller parameters
process = tdcr.to_pid_process_value(index=0)
control = pv.to_pid_control_value(index=0)
p = Pid(500)

# Define multiple schedules with different controller settings
for error_range, control_range, delta_limit, dead_zone in [
    ((-50, 50), None, 0.00005, 10),
    ((-250, 250), None, 0.0005, None),
    ((-10000, 0), None, 0.05, None),
    (None, (0, 0.3), 0.020, None),
    (None, None, 0.050, None)
]:
    controller = Controller()
    controller.kp = -1.
    controller.dead_zone = dead_zone
    controller.delta_limit = delta_limit
    cont_sched = ControllerSchedule()
    cont_sched.error = error_range
    cont_sched.control = control_range
    sched = Schedule(controller, cont_sched)
    p.add_schedule(sched)

# Set output limits for the PID controller
p.output_limits = (0.1, 1)

# Create a PID controller instance using Aqueduct
pid = aq.pid_controller("pinch_valve_control", process, control, p)
