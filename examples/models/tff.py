import typing
import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.core.units import PressureUnits
from aqueduct.devices.pump.peristaltic import PeristalticPump
from aqueduct.devices.balance import Balance
from aqueduct.devices.valve.pinch import PinchValve
from aqueduct.devices.pressure.transducer import PressureTransducer


class PressureModel:
    """
    This simple model estimates the pressures:
        - feed (between feed pump and TFF feed input)
        - retentate (between TFF retentate outlet and PV)
        - permeate (between TFF permeate outlet and permeate pump)
    using the current pump flow rates and pinch valve position
    as input parameters.

    Procedure:
        1. model Cv of the pass through (feed-retentate) leg of the TFF filter using
           P1 - P2 for known flow rates
        2. model Cv of the pinch valve using a non-linear expression that decreases
           as ~(% open)**-2 with an onset pct open of 0.3 (30%)
        3. calculate retentate pressure assuming atmospheric output pressure and using Cv pinch valve
        4. calculate feed pressure using retentate pressure and Cv TFF pass through
        5. calculate permeate pressure using the expression for TMP

    :ivar filtration_start_time: Start time of the filtration process.
    :vartype filtration_start_time: float

    :ivar filter_cv_retentate: Cv value of the retentate leg of the TFF filter.
    :vartype filter_cv_retentate: float
    """

    filter_cv_retentate: float = 60

    def calc_delta_p_feed_rententate(self, feed_rate_ml_min: float) -> float:
        """
        Calculate the pressure drop between feed and retentate.

        :param feed_rate_ml_min: Flow rate in the pass-through leg of the TFF filter.
        :type feed_rate_ml_min: float

        :return: Pressure drop between feed and retentate.
        :rtype: float
        """
        try:
            return 1 / (self.filter_cv_retentate * 0.865 / feed_rate_ml_min) ** 2
        except ZeroDivisionError:
            return 0

    @staticmethod
    def calc_pv_cv(position: float) -> float:
        """
        Calculate the Cv of the pinch valve.

        :param PV: Pinch valve position.
        :type PV: float

        :return: Cv of the pinch valve.
        :rtype: float
        """
        if position < 0.30:
            return max(100 - (1 / position**2), 1)
        else:
            return 100

    @staticmethod
    def calc_delta_p_rententate(feed_rate_ml_min, pinch_valve_position) -> float:
        """
        Calculate the pressure drop between retentate and atmospheric output.

        :param feed_rate_ml_min: Flow rate in the pass-through leg of the TFF filter.
        :type feed_rate_ml_min: float

        :param pinch_valve_position: Pinch valve position.
        :type pinch_valve_position: float

        :return: Pressure drop between retentate and permeate.
        :rtype: float
        """
        try:
            return 1 / (PressureModel.calc_pv_cv(pinch_valve_position) * 0.865 / feed_rate_ml_min) ** 2
        except ZeroDivisionError:
            return 0

    def calc_feed_pressure(self, R1, PV, P2) -> float:
        """
        Calculate the P1 pressure.

        :param R1: Flow rate in the pass-through leg of the TFF filter.
        :type R1: float

        :param PV: Pinch valve position.
        :type PV: float

        :param P2: P2 pressure.
        :type P2: float

        :return: P1 pressure.
        :rtype: float
        """
        return P2 + self.calc_delta_p_rententate(R1, PV)

    @staticmethod
    def calc_retentate_pressure(R1, PV) -> float:
        """
        Calculate the P2 pressure.

        :param R1: Flow rate in the pass-through leg of the TFF filter.
        :type R1: float

        :param PV: Pinch valve position.
        :type PV: float

        :return: P2 pressure.
        :rtype: float
        """
        return PressureModel.calc_delta_p_rententate(R1, PV)

    @staticmethod
    def calc_permeate_pressure(
        feed_pressure_psi: float,
        retentate_pressure_psi: float,
        feed_rate_ml_min: float,
        permeate_rate_ml_min: float
    ) -> float:
        """
        Calculate the P3 pressure.

        https://aiche.onlinelibrary.wiley.com/doi/epdf/10.1002/btpr.3084

        :param P1: P1 pressure.
        :type P1: float

        :param P2: P2 pressure.
        :type P2: float

        :param R1: Flow rate in the pass-through leg of the TFF filter.
        :type R1: float

        :param R3: Flow rate in the permeate leg of the TFF filter.
        :type R3: float

        :return: P3 pressure.
        :rtype: float
        """
        try:
            return (feed_pressure_psi + retentate_pressure_psi) / 2 - permeate_rate_ml_min**2 / feed_rate_ml_min * 3.9
        except ZeroDivisionError:
            return 0

    def calc_pressures(self,
                       feed_pump_ml_min: float,
                       permeate_pump_ml_min: float,
                       pinch_valve_position: float,
                       ):
        """
        Calculate and update the pressures using the model equations.
        """
        retentate_pressure = PressureModel.calc_retentate_pressure(
            feed_pump_ml_min, pinch_valve_position)

        feed_pressure = self.calc_feed_pressure(
            feed_pump_ml_min, pinch_valve_position, retentate_pressure)

        permeate_pressure = PressureModel.calc_permeate_pressure(
            feed_pressure, retentate_pressure, feed_pump_ml_min, permeate_pump_ml_min)

        feed_pressure, retentate_pressure, permeate_pressure = min(
            feed_pressure, 50), min(retentate_pressure, 50), min(permeate_pressure, 50)

        return (feed_pressure, retentate_pressure, permeate_pressure)


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
    buffer_balance_index: int = 1
    feed_balance_index: int = 0
    permeate_balance_index: int = 2

    feed_transducer_index: int = 0
    permeate_transducer_index: int = 2
    retentate_transducer_index: int = 1

    buffer_scale_error_pct: float = 0.00001
    retentate_scale_error_pct: float = 0.00001

    pressure_model: PressureModel

    def __init__(self,
                 feed_pump: PeristalticPump,
                 permeate_pump: PeristalticPump,
                 buffer_pump: typing.Union[PeristalticPump, None],
                 balances: Balance,
                 transducers: PressureTransducer,
                 pinch_valve: PinchValve
                 ):
        """Initialize the model."""
        self.feed_pump = feed_pump
        self.permeate_pump = permeate_pump
        self.buffer_pump = buffer_pump
        self.balances = balances
        self.transducers = transducers
        self.pinch_valve = pinch_valve

        self.pressure_model = PressureModel()

    def calculate(self):
        """
        Calculate the derived values for all pressure transducers and balances.
        """
        balance_rocs = [0, 0, 0, 0]

        buffer_pump_ml_min = 0

        # if BUFFER PUMP is present, use this to drive sim value balance
        if isinstance(self.buffer_pump, PeristalticPump):
            buffer_pump_ml_min = self.buffer_pump.live[0].ml_min
            balance_rocs[self.buffer_balance_index] = (-1 * buffer_pump_ml_min) * (
                1.0 + self.buffer_scale_error_pct
            )

        feed_pump_ml_min = self.feed_pump.live[0].ml_min
        permeate_pump_ml_min = self.permeate_pump.live[0].ml_min
        pv_position = self.pinch_valve.live[0].pct_open

        balance_rocs[self.permeate_balance_index] = permeate_pump_ml_min * \
            (1.0 + self.retentate_scale_error_pct)

        balance_rocs[self.feed_balance_index] = -1 * (
            balance_rocs[self.buffer_balance_index] +
            balance_rocs[self.permeate_balance_index]
        )

        # mL/min to mL/s
        balance_rocs = [r / 60.0 for r in balance_rocs]

        self.balances.set_sim_rates_of_change(balance_rocs)

        feed_pressure, retentate_pressure, permeate_pressure = self.pressure_model.calc_pressures(
            feed_pump_ml_min, permeate_pump_ml_min, pv_position)

        self.transducers.set_sim_values(
            [feed_pressure, retentate_pressure, permeate_pressure], PressureUnits.PSI)


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
    FEED_PUMP_NAME = "MFPP000001"
    BUFFER_PUMP_NAME = "MFPP000002"
    PERMEATE_PUMP_NAME = "MFPP000003"
    BALANCES_NAME = "OHSA000001"
    TRANSDUCERS_NAME = "SCIP000001"
    PINCH_VALVE_NAME = "PV000001"

    # Retrieve device instances
    feed_pump: PeristalticPump = aq.devices.get(FEED_PUMP_NAME)
    permeate_pump: PeristalticPump = aq.devices.get(PERMEATE_PUMP_NAME)
    buffer_pump: PeristalticPump = aq.devices.get(BUFFER_PUMP_NAME)
    balances: Balance = aq.devices.get(BALANCES_NAME)
    transducers: PressureTransducer = aq.devices.get(TRANSDUCERS_NAME)
    pinch_valve: PinchValve = aq.devices.get(PINCH_VALVE_NAME)

    balances.set_sim_noise([0.0001, 0.0005, 0.0001])
    transducers.set_sim_noise([0.0001, 0.0001, 0.0001])

    # Create an instance of the PressureModel
    model = Model(feed_pump, permeate_pump, buffer_pump,
                  balances, transducers, pinch_valve)

    # Continuous pressure calculation loop
    while True:
        model.calculate()
        time.sleep(0.1)
