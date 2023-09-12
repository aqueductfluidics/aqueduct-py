import typing
import time
import math

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

    filter_cv_retentate: float = .87

    @staticmethod
    def cv_from_diameter_mm(diameter: float) -> float:
        Cv = (((diameter / 1000) ** 2) * 0.61) * 46250.9
        return Cv

    @staticmethod
    def cv_from_area_mm(area_mm: float) -> float:
        # Convert the area from mm^2 to m^2
        area_m = area_mm * 1e-6
        
        # Calculate the diameter from the area
        diameter_m = math.sqrt((4 * area_m) / math.pi)

        # Calculate Cv using the given formula
        Cv = (((diameter_m) ** 2) * 0.61) * 46250.9
    
        return Cv
    
    @staticmethod
    def occluded_area_pct(delta_h: float) -> float:
        """
        Calculate the percentage change in cross-sectional area of a tube when it's squeezed, based on the change in height.

        See: https://www.hindawi.com/journals/mpe/2015/547492/

        Parameters:
        delta_h (float): The change in height due to the squeeze as a fraction of the original height (ranging from 0 to 1).

        Returns:
        float: The percentage change in the new cross-sectional area, scaled between 0 and 1. 
            1 indicates maximum occlusion (tube completely flat), 
            0 indicates no occlusion (tube retains original shape).
        """
        x = max(.5 - delta_h, 0)
        oc = math.pi * x * (math.sqrt(-20 * x**2 + 12 * x + 3) / 6 - (2 * x / 3) + 0.5)
        oc = min(-1 * (oc-0.7853981633974483), 1)
        return oc

    @staticmethod
    def calc_pv_cv(position: float) -> float:
        """
        Calculate the Cv of the pinch valve.

        :param PV: Pinch valve position.
        :type PV: float

        :return: Cv of the pinch valve.
        :rtype: float
        """
        response_zone = 0.35

        if position < response_zone:
            area = (math.pi * (5 / 2)**2)  * (1 - PressureModel.occluded_area_pct((response_zone - position)/response_zone))
            return PressureModel.cv_from_area_mm(area_mm=area)
        else:
            return 100

    @staticmethod
    def calc_delta_p_psi(mass_flow_rate_ml_min: float, cv: float) -> float:
        """
        Calculate the pressure drop between through a restriction
        using the metric equivalent flow factor (Kv) equation:

        Kv = Q * sqrt(SG / ΔP)

        Where:
        Kv : Flow factor (m^3/h)
        Q : Flowrate (m^3/h)
        SG : Specific gravity of the fluid (for water = 1)
        ΔP : Differential pressure across the device (bar)

        Kv can be calculated from Cv (Flow Coefficient) using the equation:
        Kv = 0.865 * Cv

        :param mass_flow_rate_ml_min: Flowrate.
        :type mass_flow_rate_ml_min: float

        :param cv: Flow Coefficient.
        :type cv: float

        :return: Pressure drop (psi).
        :rtype: float
        """
        try:
            kv = 0.865 * cv
            # Convert mL/min to m^3/h
            delta_p_bar = 1 / (kv / (mass_flow_rate_ml_min / 60.0)) ** 2
            delta_p_psi = delta_p_bar * 14.5038  # Convert bar to psi
            return delta_p_psi
        except ZeroDivisionError:
            return 0

    @staticmethod
    def calc_delta_p_rententate_psi(feed_rate_ml_min: float, pinch_valve_position: float) -> float:
        """
        Calculate the pressure drop between retentate and atmospheric output 
        using the metric equivalent flow factor (Kv) equation:

        :param feed_rate_ml_min: Flow rate in the pass-through leg of the TFF filter.
        :type feed_rate_ml_min: float

        :param pinch_valve_position: Pinch valve position.
        :type pinch_valve_position: float

        :return: Pressure drop between retentate and atmospheric outlet.
        :rtype: float
        """
        cv = PressureModel.calc_pv_cv(pinch_valve_position)
        return PressureModel.calc_delta_p_psi(feed_rate_ml_min, cv)

    def calc_feed_pressure_psi(self, feed_rate_ml_min: float, retentate_pressure_psi: float) -> float:
        """
        Calculate the feed pressure.

        :param feed_rate_ml_min: Flow rate in the pass-through leg of the TFF filter (ml/min).
        :type feed_rate_ml_min: float

        :param retentate_pressure_psi: Retentate pressure (psi).
        :type P2: float

        :return: P1 pressure.
        :rtype: float
        """
        return retentate_pressure_psi + self.calc_delta_p_psi(feed_rate_ml_min, PressureModel.filter_cv_retentate)

    @staticmethod
    def calc_permeate_pressure(
        feed_pressure_psi: float,
        retentate_pressure_psi: float,
        permeate_rate_ml_min: float
    ) -> float:
        """
        Calculate the permeate pressure pressure.

        https://aiche.onlinelibrary.wiley.com/doi/epdf/10.1002/btpr.3084

        :param feed_pressure_psi: Feed pressure.
        :type feed_pressure_psi: float

        :param retentate_pressure_psi: Retentate pressure.
        :type retentate_pressure_psi: float

        :param permeate_rate_ml_min: Permeate flow rate.
        :type permeate_rate_ml_min: float

        :return: Premeate pressure (psi).
        :rtype: float
        """
        try:
            avg_psi = (feed_pressure_psi + retentate_pressure_psi) / 2
            return avg_psi - permeate_rate_ml_min * .8
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
        retentate_pressure_psi = PressureModel.calc_delta_p_rententate_psi(
            feed_pump_ml_min, pinch_valve_position)

        feed_pressure_psi = self.calc_feed_pressure_psi(
            feed_pump_ml_min, retentate_pressure_psi)

        permeate_pressure_psi = PressureModel.calc_permeate_pressure(
            feed_pressure_psi, retentate_pressure_psi, permeate_pump_ml_min)

        feed_pressure, retentate_pressure, permeate_pressure = min(
            feed_pressure_psi, 50), min(retentate_pressure_psi, 50), min(permeate_pressure_psi, 50)

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
