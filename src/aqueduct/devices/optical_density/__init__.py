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
import enum
from typing import Tuple

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.units import OpticalDensityUnits


class OpticalDensityProbeLiveKeys(enum.Enum):
    """
    Enum representing the keys used in OpticalDensityProbeLive serialization/deserialization.
    """

    od = "od"
    transmitted = "t"
    ninety_deg = "n"


class OpticalDensityProbeLive:
    """
    The live representation of an optical density probe.

    Attributes:
        od (float): The optical density reading value of the probe (dimensionless).
        transmitted (float): The transmitted intensity value from the probe (counts).
        ninety_deg (float): The 90 degree scattered intensity value from the probe (counts).
    """

    mapping = {
        OpticalDensityProbeLiveKeys.od: "od",
        OpticalDensityProbeLiveKeys.transmitted: "transmitted",
        OpticalDensityProbeLiveKeys.ninety_deg: "ninety_deg",
    }

    def __init__(self, od: float, transmitted: float, ninety_deg: float):
        """
        Initialize an OpticalDensityProbeLive instance.

        Args:
            od (float): The optical density reading value of the probe (dimensionless).
            transmitted (float): The transmitted intensity value from the probe (counts).
            ninety_deg (float): The 90 degree scattered intensity value from the probe (counts).
        """
        self.od = od
        self.transmitted = transmitted
        self.ninety_deg = ninety_deg

    @classmethod
    def from_live(cls, **data) -> "OpticalDensityProbeLive":
        """
        Create an OpticalDensityProbeLive instance from the provided live data.

        Args:
            data: The live data of the optical density probe.

        Returns:
            OpticalDensityProbeLive: The created OpticalDensityProbeLive instance.
        """
        return OpticalDensityProbeLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


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

    @property
    def live(self) -> Tuple[OpticalDensityProbeLive]:
        """
        Get the live data of the optical density probe device.

        Returns:
            Tuple[OpticalDensityProbeLive]: The live data of the optical density probe device as a tuple of OpticalDensityProbeLive objects.
        """
        return self.get_live_and_cast(OpticalDensityProbeLive.from_live)

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
        l = self.live
        return (l[index].od, l[index].transmitted, l[index].ninety_deg)

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
        return self.extract_live_as_tuple_of_tuples(
            (
                OpticalDensityProbeLiveKeys.od.value,
                OpticalDensityProbeLiveKeys.transmitted.value,
                OpticalDensityProbeLiveKeys.ninety_deg.value,
            )
        )

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

    @property
    def transmitted(self) -> Tuple[float]:  # pylint: disable=invalid-name
        """
        Get the transmitted intensity values from all probes.

        Returns:
            A tuple of transmitted intensity values for all probes.
        """
        all_values = self.get_all_values()
        transmitted_values = tuple(transmitted for _, transmitted, _ in all_values)
        return transmitted_values

    @property
    def ninety_deg(self) -> Tuple[float]:  # pylint: disable=invalid-name
        """
        Get the 90 degree scattered intensity values from all probes.

        Returns:
            A tuple of 90 degree scattered intensity values for all probes.
        """
        all_values = self.get_all_values()
        ninety_deg_values = tuple(ninety_deg for _, _, ninety_deg in all_values)
        return ninety_deg_values

    def to_pid_process_value(
        self,
        index: int,
        units: OpticalDensityUnits = OpticalDensityUnits.OPTICAL_DENSITY,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The optical density units to be used (default is OpticalDensityUnits.OPTICAL_DENSITY).
        :type units: OpticalDensityUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.OpticalDensity.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
