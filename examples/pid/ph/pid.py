"""
Demonstration of setting up a PID controller with Aqueduct devices.
"""
# Import necessary modules
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.core.pid import ScheduleParameters
from aqueduct.core.pid import ScheduleConstraints
from aqueduct.core.pid import Pid
from aqueduct.core.pid import Schedule
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.ph import PhProbe

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set a delay between sending commands to the pump
aq.set_command_delay(0.05)

# Define names for devices
PUMP0_NAME = "PUMP0"
PUMP1_NAME = "PUMP1"
PUMP2_NAME = "PUMP2"
PH_PROBE_NAME = "PH_PROBE"

# Retrieve the setup to confirm the added devices
aq.get_setup()

# Retrieve device instances
pump0: PeristalticPump = aq.devices.get(PUMP0_NAME)
pump1: PeristalticPump = aq.devices.get(PUMP1_NAME)
pump2: PeristalticPump = aq.devices.get(PUMP2_NAME)
ph_probe: PhProbe = aq.devices.get(PH_PROBE_NAME)

controllers = []

for (i, pump) in enumerate([pump0, pump1, pump2]):
    # Define PID controller parameters
    process = ph_probe.to_pid_process_value(index=i)
    control = pump.to_pid_control_value(index=0)
    p = Pid(8)

    # Define multiple schedules with different controller settings
    for integral_valid, dead_zone in [
        (0.3, 0.0005),
    ]:
        params = ScheduleParameters()
        params.kp = 1
        params.ki = .025
        params.kd = .55
        params.dead_zone = dead_zone
        params.integral_valid = integral_valid
        constraints = ScheduleConstraints()
        sched = Schedule(params, constraints)
        p.add_schedule(sched)

    # Set output limits for the PID controller
    p.output_limits = (0.0, 1)

    # Create a PID controller instance using Aqueduct
    pid = aq.pid_controller(f"pump{i}", process, control, p)
    controllers.append(pid)
