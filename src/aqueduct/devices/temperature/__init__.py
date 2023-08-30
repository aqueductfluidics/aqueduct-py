import enum
from typing import List
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.units import convert_temperature_values
from aqueduct.core.units import get_temperature_conversion
from aqueduct.core.units import TemperatureUnits


class TemperatureProbeLiveKeys(enum.Enum):
    """
    Enum representing the keys used in TemperatureProbeLive serialization/deserialization.
    """

    celsius = "c"


class TemperatureProbeLive:
    """
    The live representation of a temperature probe.

    Attributes:
        celsius (float): The temperature reading value of the temperature probe in celsius.
    """

    mapping = {
        TemperatureProbeLiveKeys.celsius: "celsius",
    }

    def __init__(self, celsius: float):
        """
        Initialize a TemperatureProbeLive instance.

        Args:
            celsius (float): The temperature reading value of the temperature probe in celsius.
        """
        self.celsius = celsius

    @classmethod
    def from_live(cls, **data) -> "TemperatureProbeLive":
        """
        Create a TemperatureProbeLive instance from the provided live data.

        Args:
            data: The live data of the temperature probe.

        Returns:
            TemperatureProbeLive: The created TemperatureProbeLive instance.
        """
        return TemperatureProbeLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class TemperatureProbe(aqueduct.devices.base.obj.Device):
    """Class representing a temperature probe device.

    This class represents a temperature probe device. Methods are provided
    to read a temperature value and read all temperature values.

    :ivar has_sim_values: Flag indicating whether the device has simulated values.
    :type has_sim_values: bool
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    @property
    def live(self) -> Tuple[TemperatureProbeLive]:
        """
        Get the live data of a temperature probe device.

        Returns:
            Tuple[TemperatureProbeLive]: The live data of a temperature probe device as a tuple of TemperatureProbeLive objects.
        """
        return self.get_live_and_cast(TemperatureProbeLive.from_live)

    def value(self, index: int = 0):
        """
        Get a temperature value reading from the temperature probe device.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in celsius
        :rtype: float or None
        """
        return self.get_all_values()[index]

    def get_value(self, index: int = 0):
        """
        Alias for the `value` method.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in celsius
        :rtype: float or None
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the temperature readings from a temperature probe device.

        :return: temperature values for all inputs
        :rtype: tuple of floats
        """
        return self.extract_live_as_tuple(TemperatureProbeLiveKeys.celsius.value)

    @property
    def celsius(self) -> Tuple[float]:
        """
        Get all temperature readings from a temperature probe device in Celsius.

        :return: The temperature values for all inputs in Celsius.
        :rtype: Tuple[float]
        """
        return self.get_all_values()

    @property
    def kelvin(self) -> Tuple[float]:
        """
        Get all temperature readings from a temperature probe device in Kelvin.

        :return: The temperature values for all inputs in Kelvin.
        :rtype: Tuple[float]
        """
        return convert_temperature_values(
            self.celsius, TemperatureUnits.CELSIUS, TemperatureUnits.KELVIN
        )

    @property
    def fahrenheit(self) -> Tuple[float]:
        """
        Get all temperature readings from a temperature probe device in Fahrenheit.

        :return: The temperature values for all inputs in Fahrenheit.
        :rtype: Tuple[float]
        """
        return convert_temperature_values(
            self.celsius, TemperatureUnits.CELSIUS, TemperatureUnits.FAHRENHEIT
        )

    def set_sim_data(
        self,
        values: Union[List[Union[float, None]], tuple, None],
        roc: Union[List[Union[float, None]], tuple, None],
        noise: Union[List[Union[float, None]], tuple, None],
        units: TemperatureUnits = TemperatureUnits.CELSIUS,
    ):
        """
        Sets the simulated data for the temperature probe.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is TemperatureUnits.CELSIUS.
        :type units: TemperatureUnits
        """
        conversion = get_temperature_conversion(units, TemperatureUnits.CELSIUS)

        # pylint: disable=invalid-name
        def conversion_func1(x):
            return (x * conversion[0]) + conversion[1]

        self._set_sim_data(values, None, None, 1.0, conversion_func1)

        # pylint: disable=invalid-name
        def conversion_func2(x):
            return x * conversion[0]

        self._set_sim_data(None, roc, noise, 1.0, conversion_func2)

    def set_sim_values(
        self,
        values: Union[List[Union[float, None]], tuple],
        units: TemperatureUnits = TemperatureUnits.CELSIUS,
    ):
        """
        Sets the simulated values for the temperature probe.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated values. Default is TemperatureUnits.CELSIUS.
        :type units: TemperatureUnits
        """
        self.set_sim_data(values=values, roc=None, noise=None, units=units)

    def set_sim_rates_of_change(
        self,
        roc: Union[List[Union[float, None]], tuple],
        units: TemperatureUnits = TemperatureUnits.CELSIUS,
    ):
        """
        Sets the rates of change for the simulated values of the temperature probe.

        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param units: The units of the input values.
        :type units: TemperatureUnits
        """
        self.set_sim_data(values=None, roc=roc, noise=None, units=units)

    def set_sim_noise(
        self,
        noise: Union[List[Union[float, None]], tuple],
        units: TemperatureUnits = TemperatureUnits.CELSIUS,
    ):
        """
        Sets the noise values for the simulated data of the temperature probe.

        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is TemperatureUnits.CELSIUS.
        :type units: TemperatureUnits
        """
        self.set_sim_data(values=None, roc=None, noise=noise, units=units)

    def to_pid_process_value(
        self,
        index: int,
        units: TemperatureUnits = TemperatureUnits.CELSIUS,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The units to be used (default is TemperatureUnits.CELSIUS).
        :type units: MassFlowUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.Temperature.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
