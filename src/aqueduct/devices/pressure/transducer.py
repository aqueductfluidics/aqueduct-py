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
from typing import Tuple, Union

import aqueduct.devices.base.obj
from aqueduct.core.socket_constants import Actions
from aqueduct.core.units import PressureUnits, convert_pressure_values


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

        payload = self.to_payload(
            Actions.Tare,
            {"commands": commands},
            record
        )
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
        return self.extract_live_as_tuple("v")

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
        return convert_pressure_values(self.torr, PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD)
    
    @property
    def pascal(self):
        """
        Get all pressure readings from the pressure transducer device in pascals.

        :return: The pressure values for all inputs in pascals.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(self.torr, PressureUnits.TORR, PressureUnits.PASCAL)
    
    @property
    def bar(self):
        """
        Get all pressure readings from the pressure transducer device in bar.

        :return: The pressure values for all inputs in bar.
        :rtype: Tuple[float]
        """
        return convert_pressure_values(self.torr, PressureUnits.TORR, PressureUnits.BAR)