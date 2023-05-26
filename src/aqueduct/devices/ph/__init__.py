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
from typing import Tuple

from aqueduct.devices.base.obj import Device


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

    def value(self, index: int = 0):
        """
        Returns the pH reading of the device at the specified index.

        :param index: The index of the pH reading to retrieve.
        :type index: int
        :return: The pH value at the specified index.
        :rtype: float
        """

        live = self.get_live()
        return live[index].get('v')

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

        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            values.append(ipt.get('v'))
        return tuple(values)

    @property
    def ph(self): # pylint: disable=invalid-name
        """
        Get all of the pH readings from the device.

        :return: A tuple of pH values.
        :rtype: tuple[float]
        """
        return self.get_all_values()
