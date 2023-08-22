"""
Demo code showcasing the usage of Aqueduct for PID control of a Peristaltic Pump and Balance.
"""

# Import necessary modules
import time
from aqueduct.core.aq import Aqueduct, InitParams
from aqueduct.core.pid import Pid, PidController, Schedule, Controller, ControllerSchedule
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.balance import Balance
from aqueduct.devices.base.utils import DeviceTypes

# Parse the initialization parameters from the command line
params = InitParams.parse()

# Initialize the Aqueduct instance with the provided parameters
aq = Aqueduct(params.user_id, params.ip_address, params.port)

# Perform system initialization if specified
aq.initialize(params.init)

# Set a delay between sending commands to the pump
aq.set_command_delay(0.05)

# Define names for devices
PUMP_NAME = "PUMP"
BAL_NAME = "BALANCE"

# Clear the existing setup and add Peristaltic Pump and Balance devices
aq.clear_setup()
aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PUMP_NAME, 1)
aq.add_device(DeviceTypes.BALANCE, BAL_NAME, 1)

# Retrieve the setup to confirm the added devices
aq.get_setup()

# Retrieve PeristalticPump and Balance instances
pp: PeristalticPump = aq.devices.get(PUMP_NAME)
bal: Balance = aq.devices.get(BAL_NAME)

# Create a start command for the Peristaltic Pump
c = pp.make_start_command(mode=pp.MODE.Continuous, direction=pp.STATUS.Clockwise,
                          rate_value=1, rate_units=pp.RATE_UNITS.MlMin)
commands = pp.make_commands()
pp.set_command(commands, 0, c)
pp.start(commands=commands)

# Get process and control values for PID
process = bal.to_pid_process_value(index=0)
control = pp.to_pid_control_value(index=0)

# Create a PID controller
controller = Controller()
controller.kp = 10.
controller.kd = 5.
cont_sched = ControllerSchedule()
sched = Schedule(controller, cont_sched)
pid = Pid(20)
pid.output_limits = (0, 100)
pid.add_schedule(sched)
pid.enabled = True
pid = PidController("fill_controller", process, control, pid)

# Set noise level for simulation
bal.set_sim_noise([0,])

# Wait for some time
time.sleep(1)

# Create PID controller on Aqueduct
aq.create_pid_controller(pid)

# Perform PID control loop for a duration
start = time.monotonic_ns()
while time.monotonic_ns() < start + 30 * 1E9:
    bal.set_sim_rates_of_change([pp.get_ml_min()[0] / 60,])
    time.sleep(0.01)

# Change PID parameters and setpoint
pid.pid.schedule[0].change_parameters(kp=30, kd=10)
pid.change_setpoint(40)

# Perform PID control loop again for a duration
start = time.monotonic_ns()
while time.monotonic_ns() < start + 30 * 1E9:
    bal.set_sim_rates_of_change([pp.get_ml_min()[0] / 60,])
    time.sleep(0.01)

# Delete the created PID controller
pid.delete()
