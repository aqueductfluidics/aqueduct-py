"""
The `PhProbe` class represents a pH probe device in the Aqueduct Fluidics ecosystem.
The class inherits from the base `Device` class and provides methods
to interact with and control the pH probe device.

Example usage:

```python
# Initialize the Aqueduct core application and the pH probe device
aq = Aqueduct(user_id, ip_address, port)
ph_probe = aq.devices.get("ph_probe")

# Get a pH reading from the pH probe
ph_value = ph_probe.get_value()

# Get all pH readings from the pH probe
ph_values = ph_probe.get_all_values()
```

The example demonstrates how to use the `PhProbe` class to perform
operations such as calibrating the pH probe, obtaining a single
 pH reading, and retrieving all pH readings from the pH probe.
"""
import enum
from typing import List
from typing import Tuple
from typing import Union

from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.devices.base.obj import Device


class PhProbeLiveKeys(enum.Enum):
    """
    Enum representing the keys used in PhProbeLive serialization/deserialization.
    """

    ph = "v"


class PhProbeLive:
    """
    The live representation of a pH probe.

    Attributes:
        ph (float): The pH reading from the probe.
    """

    mapping = {
        PhProbeLiveKeys.ph: "ph",
    }

    def __init__(self, ph: float):
        """
        Initialize a PhProbeLive instance.

        Args:
            ph (float): The pH reading from the probe.
        """
        self.ph = ph

    @classmethod
    def from_live(cls, **data) -> "PhProbeLive":
        """
        Create a PhProbeLive instance from the provided live data.

        Args:
            data: The live data of the pH probe.

        Returns:
            PhProbeLive: The created PhProbeLive instance.
        """
        return PhProbeLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class PhProbe(Device):
    """
    A class representing a pH probe device.

    This class provides an interface to read pH values from a pH probe device.
    It inherits from the base `Device` class and defines additional methods specific to pH probes.

    Args:
        socket: The socket used to communicate with the Aqueduct application server.
        socket_lock: A lock used to synchronize access to the socket.
        **kwargs: Additional keyword arguments to pass to the base `Device` constructor.
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    @property
    def live(self) -> Tuple[PhProbeLive]:
        """
        Get the live data of the pH probe device.

        Returns:
            Tuple[PhProbeLive]: The live data of the pH probe device as a tuple of PhProbeLive objects.
        """
        return self.get_live_and_cast(PhProbeLive.from_live)

    def value(self, index: int = 0):
        """
        Returns the pH reading of the device at the specified index.

        :param index: The index of the pH reading to retrieve.
        :type index: int
        :return: The pH value at the specified index.
        :rtype: float
        """
        return self.get_all_values()[index]

    def get_value(self, index: int = 0) -> float:
        """
        Alias for the `value` method.

        :param index: The index of the pH reading to retrieve.
        :type index: int
        :return: The pH value at the specified index.
        :rtype: float
        """

        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Returns all of the pH readings from the device.

        :return: A tuple of pH values.
        :rtype: tuple[float]
        """
        return self.extract_live_as_tuple(PhProbeLiveKeys.ph.value)

    @property
    def ph(self):  # pylint: disable=invalid-name
        """
        Get all of the pH readings from the device.

        :return: A tuple of pH values.
        :rtype: tuple[float]
        """
        return self.get_all_values()

    def set_sim_data(
        self,
        values: Union[List[Union[float, None]], tuple, None],
        roc: Union[List[Union[float, None]], tuple, None],
        noise: Union[List[Union[float, None]], tuple, None],
    ):
        """
        Sets the simulated data for the pH probe.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        """
        self._set_sim_data(values, roc, noise, 1.0)

    def set_sim_values(
        self,
        values: Union[List[Union[float, None]], tuple],
    ):
        """
        Sets the simulated values for the pH probe.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], Tuple]
        """
        self.set_sim_data(values=values, roc=None, noise=None)

    def set_sim_rates_of_change(
        self,
        roc: Union[List[Union[float, None]], tuple],
    ):
        """
        Sets the rates of change for the simulated values of the pH probe.

        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], Tuple]
        """
        self.set_sim_data(values=None, roc=roc, noise=None)

    def set_sim_noise(
        self,
        noise: Union[List[Union[float, None]], tuple],
    ):
        """
        Sets the noise values for the simulated data of the pH probe.

        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], Tuple]
        """
        self.set_sim_data(values=None, roc=None, noise=noise)

    def to_pid_process_value(
        self,
        index: int,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.Ph.value,
            units=0,
            device_id=self._device_id,
            index=index,
        )
