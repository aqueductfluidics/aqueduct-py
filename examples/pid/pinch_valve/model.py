"""
Demo code demonstrating pressure estimation using a simple model for Aqueduct devices.
"""
# Import necessary modules
import argparse
import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.base.utils import DeviceTypes
from aqueduct.devices.pressure.transducer import PressureTransducer
from aqueduct.devices.pressure.transducer import PressureUnits
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.valve.pinch import PinchValve


class PressureModel:
    """
    Simple model for estimating pressures in a filtration process using Aqueduct devices.
    """

    filtration_start_time: float = None
    filter_cv_retentate: float = 60

    def __init__(
        self,
        pump: PeristalticPump,
        pinch_valve: PinchValve,
        transducer: PressureTransducer,
        aqueduct: "Aqueduct",
    ):
        self.pump = pump
        self.pv = pinch_valve
        self.tdcr = transducer
        self.aq = aqueduct

    @staticmethod
    def calc_pv_cv(PV) -> float:
        """
        Calculate the Cv of the pinch valve.

        :param PV: Pinch valve position.
        :type PV: float

        :return: Cv of the pinch valve.
        :rtype: float
        """
        if PV < 0.35:
            return max(100 - (1 / PV**2), 1)
        else:
            return 100

    def calc_p1(self, R1, PV) -> float:
        """
        Calculate the pressure drop between retentate and permeate.

        :param R1: Flow rate in the pass-through leg of the TFF filter.
        :type R1: float

        :param PV: Pinch valve position.
        :type PV: float

        :return: Pressure drop between retentate and permeate.
        :rtype: float
        """
        try:
            return 1 / (PressureModel.calc_pv_cv(PV) * 0.865 / R1) ** 2
        except ZeroDivisionError:
            return 0

    def calc_pressures(self):
        """
        Calculate and update the pressures using the model equations.
        """
        p1 = self.calc_p1(self.pump.live[0].ml_min, self.pv.live[0].pct_open)
        p1 = min(p1, 50)
        self.tdcr.set_sim_values(values=(p1,), units=PressureUnits.PSI)


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

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--clear",
        type=int,
        help="clear and create the setup (either 0 or 1)",
        default=1,
    )

    args, _ = parser.parse_known_args()
    clear = bool(args.clear)

    # Define names for devices
    PUMP_NAME = "PP"
    XDCR_NAME = "TDCR"
    PV_NAME = "PV"

    if clear:
        # Clear the existing setup and add devices
        aq.clear_setup()

        aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PUMP_NAME, 1)
        aq.add_device(DeviceTypes.PRESSURE_TRANSDUCER, XDCR_NAME, 1)
        aq.add_device(DeviceTypes.PINCH_VALVE, PV_NAME, 1)

    # Retrieve the setup to confirm the added devices
    aq.get_setup()

    # Retrieve device instances
    pp: PeristalticPump = aq.devices.get(PUMP_NAME)
    tdcr: PressureTransducer = aq.devices.get(XDCR_NAME)
    pv: PinchValve = aq.devices.get(PV_NAME)

    # Create an instance of the PressureModel
    model = PressureModel(pp, pv, tdcr, aq)

    # Continuous pressure calculation loop
    while True:
        model.calc_pressures()
        time.sleep(0.1)
