"""
Optical Density Probe Module.

Classes:
    OpticalDensityProbe: A class for reading optical density from a probe.

Methods:
    get_value(index: int = 0) -> Tuple[float, float, float]:
        Get the optical density, transmitted intensity, and 90 degree
        scattered intensity values for a single probe.
    get_all_values() -> Tuple[Tuple[float, float, float]]:
        Get the optical density, transmitted intensity, and 90 degree
        scattered intensity values for all connected probes.
"""
from typing import Tuple

import aqueduct.devices.base.obj


class OpticalDensityProbe(aqueduct.devices.base.obj.Device):
    """A class representing an optical density probe device.

    This class provides an interface to read optical density, transmitted,
    and 90 degree scattered intensity values
    from an optical density probe device. It inherits from the base
    `Device` class and defines additional constants and
    methods specific to optical density probes.

    Args:
        socket: The socket used to communicate with the Aqueduct application server.
        socket_lock: A lock used to synchronize access to the socket.
        **kwargs: Additional keyword arguments to pass to the base `Device` constructor.
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    def value(self, index: int = 0):
        """Get the optical density, transmitted, and 90 degree scattered intensity values from an optical density probe.

        Args:
            index: The index of the probe from which to read the values.

        Returns:
            A tuple containing the optical density, transmitted, and 90 degree scattered intensity values,
            respectively.

        Raises:
            IndexError: If the given index is out of range.
        """
        live = self.get_live()
        return (live[index].get("od"), live[index].get("t"), live[index].get("n"))

    def get_value(self, index: int = 0):
        """Alias for the `value` method.

        Args:
            index: The index of the probe from which to read the values.

        Returns:
            A tuple containing the optical density, transmitted, and 90 degree scattered intensity values,
            respectively.

        Raises:
            IndexError: If the given index is out of range.
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[Tuple[float, float, float]]:
        """Get the optical density, transmitted, and 90 degree scattered intensity values from all probes.

        Returns:
            A tuple of tuples, where each inner tuple contains the optical density, transmitted, and 90 degree
            scattered intensity values, respectively, for a single probe.
        """
        return self.extract_live_as_tuple_of_tuples(("od", "t", "n"))

    @property
    def optical_density(self) -> Tuple[float]:  # pylint: disable=invalid-name
        """
        Get the optical density values from all probes.

        Returns:
            A tuple of optical density values for all probes.
        """
        all_values = self.get_all_values()
        od_values = tuple(od for od, _, _ in all_values)
        return od_values

    def transmitted(self) -> Tuple[float]:  # pylint: disable=invalid-name
        """
        Get the transmitted intensity values from all probes.

        Returns:
            A tuple of transmitted intensity values for all probes.
        """
        all_values = self.get_all_values()
        transmitted_values = tuple(transmitted for _, transmitted, _ in all_values)
        return transmitted_values

    def ninety_deg(self) -> Tuple[float]:  # pylint: disable=invalid-name
        """
        Get the 90 degree scattered intensity values from all probes.

        Returns:
            A tuple of 90 degree scattered intensity values for all probes.
        """
        all_values = self.get_all_values()
        ninety_deg_values = tuple(ninety_deg for _, _, ninety_deg in all_values)
        return ninety_deg_values
