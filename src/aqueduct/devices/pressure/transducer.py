"""
The `PressureTransducer` class represents a pressure transducer device
in the Aqueduct Fluidics ecosystem. The class inherits from the
base `Device` class and provides methods to interact with and control the pressure transducer device.

Example usage:

```python
# Initialize the Aqueduct core application and the pressure transducer device
aq = Aqueduct(user_id, ip_address, port)
pressure_transducer = aq.devices.get("pressure_transducer")

# Tare the pressure transducer
pressure_transducer.tare()

# Get a pressure reading from the pressure transducer
pressure = pressure_transducer.get_value()

# Get all pressure readings from the pressure transducer
pressures = pressure_transducer.get_all_values()
```

The example demonstrates how to use the `PressureTransducer` class to perform
operations such as taring the pressure transducer, obtaining
a single pressure reading, and retrieving all pressure readings from the pressure transducer.
"""
import enum
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.socket_constants import Actions
from aqueduct.core.units import convert_pressure_values
from aqueduct.core.units import get_pressure_conversion
from aqueduct.core.units import PressureUnits


class PressureTransducerLiveKeys(enum.Enum):
    """
    Enum representing the keys used in PressureTransducerLive serialization/deserialization.
    """

    torr = "v"


class PressureTransducerLive:
    """
    The live representation of a pressure transducer.

    Attributes:
        torr (Optional[float]): The reading from the transducer in units of torr.
    """

    mapping = {
        PressureTransducerLiveKeys.torr: "torr",
    }

    def __init__(self, torr: Optional[float]):
        """
        Initialize a PressureTransducerLive instance.

        Args:
            torr (Optional[float]): The reading from the transducer in units of torr.
        """
        self.torr = torr

    @classmethod
    def from_live(cls, **data) -> "PressureTransducerLive":
        """
        Create a PressureTransducerLive instance from the provided live data.

        Args:
            data: The live data of the pressure transducer.

        Returns:
            PressureTransducerLive: The created PressureTransducerLive instance.
        """
        return PressureTransducerLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class PressureTransducer(aqueduct.devices.base.obj.Device):
    """Class representing a pressure transducer device.

    This class represents a pressure transducer device, which can be used to measure pressure values.
    Methods are provided to tare the device, read pressure values, and read all pressure values.

    :ivar has_sim_values: Flag indicating whether the device has simulated values.
    :type has_sim_values: bool
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    @property
    def live(self) -> Tuple[PressureTransducerLive]:
        """
        Get the live data of the pressure transducer device.

        Returns:
            Tuple[PressureTransducerLive]: The live data of the pressure transducer
            device as a tuple of PressureTransducerLive objects.
        """
        return self.get_live_and_cast(PressureTransducerLive.from_live)

    def tare(self, index: int = 0, record: Union[bool, None] = None):
        """
        Send a tare command to one of the pressure transducer inputs.

        :param index: The index of the pressure transducer input to tare.
        :type index: int

        :param record: Optional parameter indicating whether to record the tare operation.
        :type record: Union[bool, None]
        """
        commands = self.len * [None]
        commands[index] = 1

        payload = self.to_payload(Actions.Tare, {"commands": commands}, record)
        self.send_command(payload)

    def value(self, index: int = 0):
        """
        Get a pressure value reading in Torr from one of the pressure transducer inputs.

        :param index: The index of the pressure transducer input to read from (0 is the first input).
        :type index: int

        :return: The pressure value in Torr.
        :rtype: Union[float, None]
        """
        return self.get_all_values()[index]

    def get_value(self, index: int = 0):
        """
        Alias for the `value` method.

        :param index: The index of the pressure transducer input to read from (0 is the first input).
        :type index: int

        :return: The pressure value in torr.
        :rtype: Union[float, None]
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the pressure readings from the pressure transducer device.

        :return: The pressure values (in torr) for all inputs as a tuple.
        :rtype: Tuple[float]
        """
        return self.extract_live_as_tuple(PressureTransducerLiveKeys.torr.value)

    @property
    def torr(self):
        """
        Get all pressure readings from the pressure transducer device in torr.

        :return: The pressure values for all inputs in torr.
        :rtype: Tuple[float]
        """
        return self.get_all_values()

    @property
    def psi(self):
        """
        Get all pressure readings from the pressure transducer device in psi.

        :return: The pressure values for all inputs in psi.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(self.torr, PressureUnits.TORR, PressureUnits.PSI)

    @property
    def atm(self):
        """
        Get all pressure readings from the pressure transducer device in atmospheres.

        :return: The pressure values for all inputs in atmospheres.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(
            self.torr, PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD
        )

    @property
    def pascal(self):
        """
        Get all pressure readings from the pressure transducer device in pascals.

        :return: The pressure values for all inputs in pascals.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(
            self.torr, PressureUnits.TORR, PressureUnits.PASCAL
        )

    @property
    def bar(self):
        """
        Get all pressure readings from the pressure transducer device in bar.

        :return: The pressure values for all inputs in bar.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(self.torr, PressureUnits.TORR, PressureUnits.BAR)

    def set_sim_data(
        self,
        values: Union[List[Union[float, None]], tuple, None],
        roc: Union[List[Union[float, None]], tuple, None],
        noise: Union[List[Union[float, None]], tuple, None],
        units: PressureUnits = PressureUnits.TORR,
    ):
        """
        Sets the simulated data for the pressure transducer.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is PressureUnits.TORR.
        :type units: PressureUnits
        """
        scale = 1.0 / get_pressure_conversion(PressureUnits.TORR, units)
        self._set_sim_data(values, roc, noise, scale)

    def set_sim_values(
        self,
        values: Union[List[Union[float, None]], tuple],
        units: PressureUnits = PressureUnits.TORR,
    ):
        """
        Sets the simulated values for the pressure transducer.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated values. Default is PressureUnits.TORR.
        :type units: PressureUnits
        """
        self.set_sim_data(values=values, roc=None, noise=None, units=units)

    def set_sim_rates_of_change(
        self,
        roc: Union[List[Union[float, None]], tuple],
        units: PressureUnits = PressureUnits.TORR,
    ):
        """
        Sets the rates of change for the simulated values of the pressure transducer.

        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param units: The units of the input values.
        :type units: PressureUnits
        """
        self.set_sim_data(values=None, roc=roc, noise=None, units=units)

    def set_sim_noise(
        self,
        noise: Union[List[Union[float, None]], tuple],
        units: PressureUnits = PressureUnits.TORR,
    ):
        """
        Sets the noise values for the simulated data of the pressure transducer.

        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        :param units: The units for the simulated data. Default is PressureUnits.TORR.
        :type units: PressureUnits
        """
        self.set_sim_data(values=None, roc=None, noise=noise, units=units)

    def to_pid_process_value(
        self,
        index: int,
        units: PressureUnits = PressureUnits.TORR,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The pressure units to be used (default is PressureUnits.TORR).
        :type units: PressureUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.Pressure.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
