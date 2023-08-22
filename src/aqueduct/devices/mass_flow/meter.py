import enum
from typing import List
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.units import convert_mass_flow_values
from aqueduct.core.units import get_mass_flow_conversion
from aqueduct.core.units import MassFlowUnits


class MassFlowMeterLiveKeys(enum.Enum):
    """
    Enum representing the keys used in MassFlowMeterLive serialization/deserialization.
    """

    ml_min = "v"


class MassFlowMeterLive:
    """
    The live representation of a mass flow meter.

    Attributes:
        mL/min (float): The mass flow reading value of the mass flow meter in mL/min.
    """

    mapping = {
        MassFlowMeterLiveKeys.ml_min: "ml_min",
    }

    def __init__(self, ml_min: float):
        """
        Initialize a MassFlowMeterLive instance.

        Args:
            mL/min (float): The mass flow reading value of the mass flow meter in mL/min.
        """
        self.ml_min = ml_min

    @classmethod
    def from_live(cls, **data) -> "MassFlowMeterLive":
        """
        Create a MassFlowMeterLive instance from the provided live data.

        Args:
            data: The live data of the mass flow meter.

        Returns:
            MassFlowMeterLive: The created MassFlowMeterLive instance.
        """
        return MassFlowMeterLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class MassFlowMeter(aqueduct.devices.base.obj.Device):
    """Class representing a mass flow meter device.

    This class represents a mass flow meter device, which can be used to weigh substances. Methods are provided
    to tare the device, read a mass flow value, and read all mass flow values.

    :ivar has_sim_values: Flag indicating whether the device has simulated values.
    :type has_sim_values: bool
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    @property
    def live(self) -> Tuple[MassFlowMeterLive]:
        """
        Get the live data of a mass flow meter device.

        Returns:
            Tuple[MassFlowMeterLive]: The live data of a mass flow meter device as a tuple of MassFlowMeterLive objects.
        """
        return self.get_live_and_cast(MassFlowMeterLive.from_live)

    def value(self, index: int = 0):
        """
        Get a mass flow value reading from the mass flow meter device.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in mL/min
        :rtype: float or None
        """
        return self.get_all_values()[index]

    def get_value(self, index: int = 0):
        """
        Alias for the `value` method.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in mL/min
        :rtype: float or None
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the mass flow readings from a mass flow meter device.

        :return: mass flow values for all inputs
        :rtype: tuple of floats
        """
        return self.extract_live_as_tuple(MassFlowMeterLiveKeys.ml_min.value)

    @property
    def ml_min(self) -> Tuple[float]:
        """
        Get all mass flow readings from a mass flow meter device in mL/min.

        :return: The mass flow values for all inputs in mL/min.
        :rtype: Tuple[float]
        """
        return self.get_all_values()

    @property
    def ul_min(self) -> Tuple[float]:
        """
        Get all mass flow readings from a mass flow meter device in uL/min.

        :return: The mass flow values for all inputs in uL/min.
        :rtype: Tuple[float]
        """
        return convert_mass_flow_values(
            self.ml_min, MassFlowUnits.ML_MIN, MassFlowUnits.UL_MIN
        )

    @property
    def ml_hr(self) -> Tuple[float]:
        """
        Get all mass flow readings from a mass flow meter device in mL/hr.

        :return: The mass flow values for all inputs in mL/hr.
        :rtype: Tuple[float]
        """
        return convert_mass_flow_values(
            self.ml_min, MassFlowUnits.ML_MIN, MassFlowUnits.ML_HR
        )

    @property
    def ul_hr(self) -> Tuple[float]:
        """
        Get all mass flow readings from a mass flow meter device in uL/hr.

        :return: The mass flow values for all inputs in uL/hr.
        :rtype: Tuple[float]
        """
        return convert_mass_flow_values(
            self.ml_min, MassFlowUnits.ML_MIN, MassFlowUnits.UL_HR
        )

    def set_sim_data(
        self,
        values: Union[List[Union[float, None]], tuple, None],
        roc: Union[List[Union[float, None]], tuple, None],
        noise: Union[List[Union[float, None]], tuple, None],
        units: MassFlowUnits = MassFlowUnits.ML_MIN,
    ):
        """
        Sets the simulated data for the mass flow meter.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], tuple, None]
        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], tuple, None]
        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], tuple, None]
        :param units: The units for the simulated data. Default is MassFlowUnits.ML_MIN.
        :type units: MassFlowUnits
        """
        scale = 1.0 / get_mass_flow_conversion(MassFlowUnits.ML_MIN, units)
        self._set_sim_data(values, roc, noise, scale)

    def set_sim_values(
        self,
        values: Union[List[Union[float, None]], tuple],
        units: MassFlowUnits = MassFlowUnits.ML_MIN,
    ):
        """
        Sets the simulated values for the mass flow meter.

        :param values: The simulated values.
        :type values: Union[List[Union[float, None]], tuple]
        :param units: The units for the simulated values. Default is MassFlowUnits.ML_MIN.
        :type units: MassFlowUnits
        """
        self.set_sim_data(values=values, roc=None, noise=None, units=units)

    def set_sim_rates_of_change(
        self,
        roc: Union[List[Union[float, None]], tuple],
        units: MassFlowUnits = MassFlowUnits.ML_MIN,
    ):
        """
        Sets the rates of change for the simulated values of the mass flow meter.

        :param roc: The rates of change for the simulated values.
        :type roc: Union[List[Union[float, None]], tuple]
        :param units: The units of the input values. Default is MassFlowUnits.ML_MIN.
        :type units: MassFlowUnits
        """
        self.set_sim_data(values=None, roc=roc, noise=None, units=units)

    def set_sim_noise(
        self,
        noise: Union[List[Union[float, None]], tuple],
        units: MassFlowUnits = MassFlowUnits.ML_MIN,
    ):
        """
        Sets the noise values for the simulated data of the mass flow meter.

        :param noise: The noise values for the simulated data.
        :type noise: Union[List[Union[float, None]], tuple]
        :param units: The units for the simulated data. Default is MassFlowUnits.ML_MIN.
        :type units: MassFlowUnits
        """
        self.set_sim_data(values=None, roc=None, noise=noise, units=units)

    def to_pid_process_value(
        self,
        index: int,
        units: MassFlowUnits = MassFlowUnits.ML_MIN,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The units to be used (default is MassFlowUnits.ML_MIN).
        :type units: MassFlowUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.MassFlow.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
