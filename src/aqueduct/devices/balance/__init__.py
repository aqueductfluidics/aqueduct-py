"""
The `Balance` class represents a balance device in the Aqueduct Fluidics
ecosystem. The `Balance` class inherits from the base `Device` class and
provides methods to interact with and control the balance device.

Example usage:

    # initialize the Aqueduct core application and the balance device
    aq = Aqueduct(user_id, ip_address, port)
    balance = aq.devices.get("balance")

    # tare the balance
    balance.tare()

    # zero the balance
    balance.zero()

    # get a weight reading from the balance
    weight = balance.get_value()

    # get all weight readings from the balance
    weights = balance.get_all_values()

"""
import enum
from typing import List
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.socket_constants import Actions
from aqueduct.core.units import convert_weight_values
from aqueduct.core.units import get_weight_conversion
from aqueduct.core.units import WeightUnits


class BalanceLiveKeys(enum.Enum):
    """
    Enum representing the keys used in BalanceLive serialization/deserialization.
    """

    grams = "g"


class BalanceLive:
    """
    The live representation of a balance.

    Attributes:
        grams (float): The weight reading value of the balance in grams.
    """

    mapping = {
        BalanceLiveKeys.grams: "grams",
    }

    def __init__(self, grams: float):
        """
        Initialize a BalanceLive instance.

        Args:
            grams (float): The weight reading value of the balance in grams.
        """
        self.grams = grams

    @classmethod
    def from_live(cls, **data) -> "BalanceLive":
        """
        Create a BalanceLive instance from the provided live data.

        Args:
            data: The live data of the balance.

        Returns:
            BalanceLive: The created BalanceLive instance.
        """
        return BalanceLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class Balance(aqueduct.devices.base.obj.Device):
    """Class representing a balance device.

    This class represents a balance device, which can be used to weigh substances. Methods are provided
    to tare the device, read a weight value, and read all weight values.

    :ivar has_sim_values: Flag indicating whether the device has simulated values.
    :type has_sim_values: bool
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    @property
    def live(self) -> Tuple[BalanceLive]:
        """
        Get the live data of a balance device.

        Returns:
            Tuple[BalanceLive]: The live data of a balance device as a tuple of BalanceLive objects.
        """
        return self.get_live_and_cast(BalanceLive.from_live)

    def tare(self, index: int = 0, record: Union[bool, None] = None):
        """
        Send a tare command to the balance device.

        :param index: number-like value to specify the input of the balance to tare
        :type index: int
        """
        commands = self.len * [None]
        commands[index] = 1

        payload = self.to_payload(Actions.Tare, {"commands": commands}, record)
        self.send_command(payload)

    def zero(self, index: int = 0, record: Union[bool, None] = None):
        """
        Send a zero command to the balance device.

        :param index: number-like value to specify the input of the balance to zero
        :type index: int
        """
        commands = self.len * [None]
        commands[index] = 1

        payload = self.to_payload(Actions.Zero, {"commands": commands}, record)
        self.send_command(payload)

    def value(self, index: int = 0):
        """
        Get a weight value reading from the balance device.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in grams
        :rtype: float or None
        """
        return self.get_all_values()[index]

    def get_value(self, index: int = 0):
        """
        Alias for the `value` method.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in grams
        :rtype: float or None
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the weight readings from a balance device.

        :return: weight values for all inputs
        :rtype: tuple of floats
        """
        return self.extract_live_as_tuple(BalanceLiveKeys.grams.value)

    @property
    def grams(self) -> Tuple[float]:
        """
        Get all weight readings from a balance device in grams.

        :return: The weight values for all inputs in grams.
        :rtype: Tuple[float]
        """
        return self.get_all_values()

    @property
    def kilograms(self) -> Tuple[float]:
        """
        Get all weight readings from a balance device in kilograms.

        :return: The weight values for all inputs in kilograms.
        :rtype: Tuple[float]
        """
        return convert_weight_values(
            self.grams, WeightUnits.GRAMS, WeightUnits.KILOGRAMS
        )

    @property
    def pounds(self) -> Tuple[float]:
        """
        Get all weight readings from a balance device in pounds.

        :return: The weight values for all inputs in pounds.
        :rtype: Tuple[float]
        """
        return convert_weight_values(self.grams, WeightUnits.GRAMS, WeightUnits.POUNDS)

    @property
    def newtons(self) -> Tuple[float]:
        """
        Get all weight readings from a balance device in newtons.

        :return: The weight values for all inputs in newtons.
        :rtype: Tuple[float]
        """
        return convert_weight_values(self.grams, WeightUnits.GRAMS, WeightUnits.NEWTONS)

    @property
    def ounces(self) -> Tuple[float]:
        """
        Get all weight readings from a balance device in ounces.

        :return: The weight values for all inputs in ounces.
        :rtype: Tuple[float]
        """
        return convert_weight_values(self.grams, WeightUnits.GRAMS, WeightUnits.OUNCES)

    def set_sim_data(
        self,
        values: Union[List[Union[float, None]], tuple, None],
        roc: Union[List[Union[float, None]], tuple, None],
        noise: Union[List[Union[float, None]], tuple, None],
        units: WeightUnits = WeightUnits.GRAMS,
    ):
        """
        Sets the simulated data for the balance.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is WeightUnits.GRAMS.
        :type units: WeightUnits
        """
        scale = 1.0 / get_weight_conversion(WeightUnits.GRAMS, units)
        self._set_sim_data(values, roc, noise, scale)

    def set_sim_values(
        self,
        values: Union[List[Union[float, None]], tuple],
        units: WeightUnits = WeightUnits.GRAMS,
    ):
        """
        Sets the simulated values for the balance.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated values. Default is WeightUnits.GRAMS.
        :type units: WeightUnits
        """
        self.set_sim_data(values=values, roc=None, noise=None, units=units)

    def set_sim_rates_of_change(
        self,
        roc: Union[List[Union[float, None]], tuple],
        units: WeightUnits = WeightUnits.GRAMS,
    ):
        """
        Sets the rates of change for the simulated values of the balance.

        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param units: The units of the input values.
        :type units: WeightUnits
        """
        self.set_sim_data(values=None, roc=roc, noise=None, units=units)

    def set_sim_noise(
        self,
        noise: Union[List[Union[float, None]], tuple],
        units: WeightUnits = WeightUnits.GRAMS,
    ):
        """
        Sets the noise values for the simulated data of the balance.

        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is WeightUnits.GRAMS.
        :type units: WeightUnits
        """
        self.set_sim_data(values=None, roc=None, noise=noise, units=units)

    def to_pid_process_value(
        self,
        index: int,
        units: WeightUnits = WeightUnits.GRAMS,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The weight units to be used (default is WeightUnits.GRAMS).
        :type units: WeightUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.Weight.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
