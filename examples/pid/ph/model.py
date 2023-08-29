"""
Description: This script models a chemical reaction system using threads for parallel calculations.
It simulates the delay in the response of pH with respect to the change in dose rate, thereby
modeling a time constant in the system.
"""

import time
import typing
import random
import threading

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.base.utils import DeviceTypes
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.ph import PhProbe


class Reaction:
    """
    Models a single chemical reaction by defining parameters to capture
    the rate of change of pH as a function of dose rate (mL/min).

    Attributes:
        reaction_start_time: Time when the reaction started.
        dpH_s_dmL_min_start: Initial slope of pH change per mL/min rate.
        delta_change_s: Change in slope of pH change per second.
        delta_change_bounds: Maximum and minimum rate of change.
        roc_offset: Initial offset of the rate of change.
        last_roc: Last calculated rate of change.
        time_constant_s: Time constant to model delay in pH response.
    """

    def __init__(self):
        """Initialize reaction parameters."""
        self.time_constant_s = round(random.uniform(2, 6), 3)
        self.roc_offset = round(random.uniform(-1.95 / 60, -0.95 / 60), 4)
        self.reaction_start_time: float = None

        self.dpH_s_dmL_min_start: float = 0.095  # (pH/s)/(mL/min)
        self.delta_change_s: float = 0.000005  # (pH/s)/(mL/min*s)
        self.delta_change_bounds: tuple = (-0.5, 0.5)

        self.last_roc = None

    def start_reaction(self) -> None:
        """Record the starting time of the reaction."""
        self.reaction_start_time = time.time()

    def calc_rate_of_change(self, ml_min):
        """
        Calculate the rate of change of pH with respect to the dose rate (mL/min).

        Args:
            ml_min: The dosing rate in mL/min.
        """
        # Calculate the time since the reaction started
        reaction_duration_s = time.time() - self.reaction_start_time
        
        # Calculate rate of change (roc)
        roc = self.roc_offset + (self.dpH_s_dmL_min_start +
                                 reaction_duration_s * self.delta_change_s) * ml_min
        
        # Constrain roc within bounds
        roc = max(min(roc, self.delta_change_bounds[1]),
                  self.delta_change_bounds[0])
        roc = round(roc, 4)
        self.last_roc = roc


class Model:
    """
    Main class to manage multiple Reactions and link them with physical devices.

    Attributes:
        reactions: List of Reaction objects.
        delayed_roc: List of delayed rate of change values.
        pumps: List of PeristalticPump objects.
        ph_probe: PhProbe object.
        lock: Threading lock to control concurrent access to shared resources.
    """

    def __init__(self, pumps: typing.List[PeristalticPump], probe: PhProbe):
        """Initialize the model."""
        self.pumps = pumps
        self.ph_probe = probe
        self.reactions = [None] * self.ph_probe.len
        self.lock = threading.Lock()

        for i in range(self.ph_probe.len):
            self.reactions[i] = Reaction()
            self.reactions[i].start_reaction()

    def calculate(self):
        """
        Calculate the rate of change in pH for each reaction and update the pH probe simulation.
        """
        rates = [p.live[0].ml_min for p in self.pumps]

        def target(i, m):
            """Target function for threading."""
            time.sleep(m.time_constant_s)
            with self.lock:  # Acquire the lock before updating shared data
                m.calc_rate_of_change(rates[i])

        threads = []
        for (i, m) in enumerate(self.reactions):
            t = threading.Thread(target=target, args=(i, m), daemon=True)
            threads.append(t)
            t.start()

        with self.lock:  # Acquire the lock before updating shared data
            self.ph_probe.set_sim_rates_of_change([
                r.last_roc for r in self.reactions
            ])


if __name__ == "__main__":

    # Parse the initialization parameters from the command line
    params = InitParams.parse()

    # Initialize the Aqueduct instance with the provided parameters
    aq = Aqueduct(
        params.user_id,
        params.ip_address,
        params.port,
        register_process=params.register_process,
    )

    # Perform system initialization if specified
    aq.initialize(params.init)

    # Set a delay between sending commands to the pump
    aq.set_command_delay(0.05)

    # Define names for devices
    PUMP0_NAME = "PUMP0"
    PUMP1_NAME = "PUMP1"
    PUMP2_NAME = "PUMP2"
    PH_PROBE_NAME = "PH_PROBE"

    # Clear the existing setup and add devices
    aq.clear_setup()

    aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PUMP0_NAME, 1)
    aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PUMP1_NAME, 1)
    aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PUMP2_NAME, 1)
    aq.add_device(DeviceTypes.PH_PROBE, PH_PROBE_NAME, 3)

    # Retrieve the setup to confirm the added devices
    aq.get_setup()

    # Retrieve device instances
    pump0: PeristalticPump = aq.devices.get(PUMP0_NAME)
    pump1: PeristalticPump = aq.devices.get(PUMP1_NAME)
    pump2: PeristalticPump = aq.devices.get(PUMP2_NAME)
    ph_probe: PhProbe = aq.devices.get(PH_PROBE_NAME)

    ph_probe.set_sim_noise([0.0001, 0.0005, 0.0001])
    ph_probe.set_sim_rates_of_change([-.1, -.1, -.1])

    # Create an instance of the PressureModel
    model = Model([pump0, pump1, pump2], ph_probe)

    # Continuous pressure calculation loop
    while True:
        model.calculate()
        time.sleep(0.5)
