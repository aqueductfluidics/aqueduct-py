"""PeristalticPump Module."""
import enum
from typing import List
from typing import Tuple
from typing import Union

from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.socket_constants import Actions
from aqueduct.devices.base.obj import Command
from aqueduct.devices.base.obj import DeviceKeys
from aqueduct.devices.base.obj import Device
from aqueduct.devices.base.obj import DeviceConfigInnerKeys
from aqueduct.devices.base.obj import DeviceConfigKeys

from .types import Config
from .types import aqueduct
from .types import masterflex


# pylint: disable=invalid-name
class Mode(enum.IntEnum):
    """Operational Mode of the `PeristalticPump`. Use this value to set the operation to continuous or finite."""

    Continuous = 0
    Finite = 1


# pylint: disable=invalid-name
class Status(enum.IntEnum):
    """Status of the `PeristalticPump`. Use this value to set a direction."""

    Stopped = 0
    Clockwise = 1
    CounterClockwise = 2

    def reverse(self) -> "Status":
        """Returns the opposite direction of the current `Status`.

        If the current `Status` is Clockwise, it returns CounterClockwise.
        If the current `Status` is CounterClockwise, it returns Clockwise.
        For all other values, it returns the current `Status`.

        Returns:
            Status: The opposite direction of the current `Status`.
        """
        if self == Status.Clockwise:
            return Status.CounterClockwise
        elif self == Status.CounterClockwise:
            return Status.Clockwise
        else:
            return self


# pylint: disable=invalid-name
class RateUnits(enum.IntEnum):
    """Rate units used when starting or changing the speed of a `PeristalticPump`."""

    Rpm = 0
    UlMin = 1
    UlHr = 2
    MlMin = 3
    MlHr = 4


# pylint: disable=invalid-name
class FiniteUnits(enum.IntEnum):
    """Units used when starting the pump for a `finite` mode operation."""

    Steps = 0
    Seconds = 1
    Minutes = 2
    Degrees = 3
    Ml = 4
    Ul = 5
    Revolutions = 6


class StartCommand(Command):
    """
    Command to start the peristaltic pump.

    Attributes:
        mode (Mode): Operational mode of the pump (Continuous or Finite).
        direction (Status): Direction of the pump (Clockwise or CounterClockwise).
        rate_value (Union[float, int]): Speed of the pump.
        rate_units (RateUnits): Units of the speed (e.g., Rpm, MlMin).
        finite_value (Union[float, int, None], optional): Value for finite mode operation. Defaults to None.
        finite_units (Union[FiniteUnits, None], optional): Units for finite mode operation. Defaults to None.
    """
    mode: Mode
    direction: Status
    rate_value: Union[float, int]
    rate_units: RateUnits
    finite_value: Union[float, int, None] = None
    finite_units: Union[FiniteUnits, None] = None

    def __init__(
        self,
        mode: Mode,
        direction: Status,
        rate_value: Union[float, int],
        rate_units: RateUnits,
        finite_value: Union[float, int, None] = None,
        finite_units: Union[FiniteUnits, None] = None,
    ):
        self.mode = mode
        self.direction = direction
        self.rate_value = rate_value
        self.rate_units = rate_units
        self.finite_value = finite_value
        self.finite_units = finite_units

    def to_command(self):
        """
        Converts the StartCommand object to a tuple.

        Returns:
            tuple: A tuple containing the command attributes.
        """
        return (
            self.mode,
            self.direction,
            self.rate_units,
            self.rate_value,
            self.finite_value,
            self.finite_units,
        )


class StopCommand(Command):
    """
    Command to stop the peristaltic pump.

    Attributes:
        stop (int): Stop command indicator.
    """
    stop: int

    def __init__(self, **kwargs):
        self.stop = 0

        for k, v in kwargs.items():
            if k in self.__dict__.keys():
                if v is not None:
                    setattr(self, k, v)

    def to_command(self):
        """
        Converts the StopCommand object to an integer.

        Returns:
            int: Stop command indicator.
        """
        return self.stop


class ChangeSpeedCommand(Command):
    """
    Command to change the speed of the peristaltic pump.

    Attributes:
        rate_value (Union[float, int]): New speed of the pump.
        rate_units (RateUnits): Units of the new speed (e.g., Rpm, MlMin).
    """
    rate_value: Union[float, int]
    rate_units: RateUnits

    def __init__(self, rate_value: Union[float, int], rate_units: RateUnits):
        self.rate_value = rate_value
        self.rate_units = rate_units

    def to_command(self):
        """
        Converts the ChangeSpeedCommand object to a tuple.

        Returns:
            tuple: A tuple containing the rate units and rate value.
        """
        return self.rate_units, self.rate_value


class PeristalticPumpLiveKeys(enum.Enum):
    """
    Enum representing the keys used in PeristalticPumpLive serialization/deserialization.
    """

    ml_target = "mt"
    ml_done = "md"
    ml_min = "mm"
    status = "s"
    mode = "m"


class PeristalticPumpLive:
    """The live representation of a peristaltic pump."""

    mapping = {
        PeristalticPumpLiveKeys.ml_target: "ml_target",
        PeristalticPumpLiveKeys.ml_done: "ml_done",
        PeristalticPumpLiveKeys.ml_min: "ml_min",
        PeristalticPumpLiveKeys.status: "status",
        PeristalticPumpLiveKeys.mode: "mode",
    }

    ml_target: float
    ml_done: float
    ml_min: float
    status: int
    mode: int

    def __init__(
        self, ml_target: float, ml_done: float, ml_min: float, status: int, mode: int
    ):
        """
        Initializes a PeristalticPumpLive object.

        Args:
            ml_target (float): The target volume in milliliters.
            ml_done (float): The volume already dispensed in milliliters.
            ml_min (float): The minimum flow rate in milliliters per minute.
            status (int): The status of the peristaltic pump.
            mode (int): The operational mode of the peristaltic pump.
        """
        self.ml_target = ml_target
        self.ml_done = ml_done
        self.ml_min = ml_min
        self.status = status
        self.mode = mode

    @classmethod
    def from_live(cls, **data) -> "PeristalticPumpLive":
        return PeristalticPumpLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class PeristalticPump(Device):
    """PeristalticPump class."""

    STATUS = Status
    MODE = Mode
    RATE_UNITS = RateUnits
    FINITE_UNITS = FiniteUnits

    @property
    def live(self) -> Tuple[PeristalticPumpLive]:
        """
        Get the live data of the peristaltic pump.

        Returns:
            Tuple[PeristalticPumpLive]: The live data of the peristaltic pump as a tuple of PeristalticPumpLive objects.
        """
        return self.get_live_and_cast(PeristalticPumpLive.from_live)

    @property
    def config(self) -> Union[tuple, None]:
        """
        Get the configuration data for the syringe pump device.

        This property retrieves the device configuration and casts it to the appropriate types.

        :return: The device configuration data.
        :rtype: Union[tuple, None]
        """

        def cast_config(data):
            if (
                data
                and data.get(DeviceConfigKeys.Type.value) == Config.StepperMotor.value
            ):
                configs = []
                for _i, d in enumerate(
                    data.get(DeviceConfigKeys.Config.value).get(
                        DeviceConfigInnerKeys.Data.value
                    )
                ):
                    configs.append(aqueduct.StepperMotorConfig(**d))
                data[DeviceConfigKeys.Config.value][
                    DeviceConfigInnerKeys.Data.value
                ] = configs
                return data
            elif (
                data
                and data.get(DeviceConfigKeys.Type.value) == Config.MixedSignal.value
            ):
                configs = []
                for _i, d in enumerate(
                    data.get(DeviceConfigKeys.Config.value).get(
                        DeviceConfigInnerKeys.Data.value
                    )
                ):
                    configs.append(masterflex.MixedSignal(**d))
                data[DeviceConfigKeys.Config.value][
                    DeviceConfigInnerKeys.Data.value
                ] = configs
                return data
            else:
                return data

        return self.get_config_and_cast(cast_config)

    def set_config(
        self,
        config: List[Union[aqueduct.StepperMotorConfig, masterflex.MixedSignal]],
    ):
        """
        Update the peristaltic pump configuration based on modifications.

        Only fields set in the modifications (not None) will be updated.

        :param modifications: A list of configuration class instances with modifications.
        :param record: Whether to record the command. If None, the default setting is used.
        """

        def apply_modifications(current_config, modifications):
            updated_config = []  # This will be your updated configuration payload

            # Iterate over both current_config and modifications simultaneously
            for i, current in enumerate(current_config):
                if i < len(modifications):
                    modification = modifications[i]
                    if isinstance(current, dict):
                        current_dict = current
                    else:
                        current_dict = current.to_dict()

                    mod_dict = modification.to_dict()

                    # Update fields in current_dict with those in mod_dict
                    for key, value in mod_dict.items():
                        # Only update modified fields
                        if value is not None and value != current_dict.get(key):
                            current_dict[key] = value

                    updated_config.append(current_dict)
                else:
                    updated_config.append({})

            return updated_config

        # Fetch the current configuration from the device.
        current_config = self.config.get(
            DeviceConfigKeys.Config.value).get(DeviceConfigInnerKeys.Data.value)

        # Construct a new configuration based on modifications.
        updated_config = apply_modifications(
            current_config, config)

        payload = self.to_payload(
            Actions.SetConfig,
            {DeviceKeys.Config.value: updated_config,
                DeviceKeys.Base.value: {}, DeviceKeys.Stat.value: []},
        )

        self.send_command(payload)

    def start(
        self,
        commands: List[Union[StartCommand, None]],
        record: Union[bool, None] = None,
    ) -> dict:
        """Command to start one or more pump inputs in either finite or continuous mode.

        :Example:

        .. code-block:: python

            commands = pump.make_commands()
            command = pump.make_start_command(
                mode=pump.MODE.Continuous,
                rate_units=pump.RATE_UNITS.MlMin,
                rate_value=2,
                direction=pump.STATUS.Clockwise)
            pump.set_command(commands, 0, command)
            pump.start(commands)

        :param commands: List[Union[StartCommand, None]]

        :return: None
        :rtype: None
        """
        commands = self.map_commands(commands)
        payload = self.to_payload(
            Actions.Start, {"commands": commands}, record)
        self.send_command(payload)

    def change_speed(
        self,
        commands: List[Union[ChangeSpeedCommand, None]],
        record: Union[bool, None] = None,
    ) -> dict:
        """Command to change the speed of one or more pump inputs.

        .. code-block:: python

            commands = pump.make_commands()
            command = pump.make_change_speed_command(
                rate_value=i, rate_units=pump.RATE_UNITS.MlMin)
            pump.set_command(commands, 0, command)
            pump.change_speed(commands)

        :param commands: List[Union[ChangeSpeedCommand, None]]

        :param commands:

        :return: None
        :rtype: None
        """
        commands = self.map_commands(commands)
        payload = self.to_payload(Actions.ChangeSpeed, {
                                  "commands": commands}, record)
        self.send_command(payload)

    def stop(
        self,
        commands: Union[List[Union[ChangeSpeedCommand, None]], None] = None,
    ) -> dict:
        """Stop one or more pump inputs.

        .. code-block:: python

            commands = pump.make_commands()
            command = pump.make_stop_command()
            pump.set_command(commands, 0, command)
            pump.stop(commands)

        :param commands: Union[List[Union[ChangeSpeedCommand, None]], None]

        :param commands:

        :return: None
        :rtype: None
        """
        if commands is None:
            commands = self.make_commands()
            commands = [self.make_stop_command() for _ in commands]

        commands = self.map_commands(commands)

        payload = self.to_payload(
            Actions.Stop,
            {"commands": commands},
        )
        self.send_command(payload)

    @staticmethod
    def make_start_command(
        mode: Mode,
        direction: Status,
        rate_value: Union[float, int],
        rate_units: RateUnits,
        finite_value: Union[float, int, None] = None,
        finite_units: Union[FiniteUnits, None] = None,
    ) -> StartCommand:
        """Helper method to create an instance of a :class:`PumpCommand`.

        A :class:`PumpCommand` is an object with the required fields to set the operation
        parameters for a pump input.

        :return: pump_command
        :rtype: PumpCommand
        """
        return StartCommand(
            mode, direction, rate_value, rate_units, finite_value, finite_units
        )

    @staticmethod
    def make_stop_command() -> StopCommand:
        """Helper method to create an instance of a :class:`StopCommand`.

        A :class:`StopCommand` is an object with the required fields to stop a pump input.

        :return: StopCommand
        :rtype: StopCommand
        """
        return StopCommand(stop=1)

    @staticmethod
    def make_change_speed_command(
        rate_value: Union[float, int], rate_units: RateUnits
    ) -> ChangeSpeedCommand:
        """Helper method to create an instance of a :class:`PumpCommand`.

        A :class:`PumpCommand` is an object with the required fields to set the operation
        parameters for a pump input.

        :return: pump_command
        :rtype: PumpCommand
        """
        return ChangeSpeedCommand(rate_value, rate_units)

    def get_ml_min(self) -> Tuple[float]:
        """
        Get all of the displacement rate values (in mL/min) for the peristaltic pump.

        :Example: Read all pumps:

        .. code-block:: python

            ml_min_values = pump.get_ml_min()
            len(ml_min_values)  # == pump.len

        :return: Displacement rate values in mL/min.
        :rtype: tuple
        """
        return self.extract_live_as_tuple(PeristalticPumpLiveKeys.ml_min.value)

    def get_ml_done(self) -> Tuple[float]:
        """
        Get the volume dispensed by the peristaltic pump in milliliters.

        :return: Volume dispensed in milliliters.
        :rtype: tuple
        """
        return self.extract_live_as_tuple(PeristalticPumpLiveKeys.ml_done.value)

    def to_pid_control_output(
        self,
        index: int,
        units: RateUnits = RateUnits.MlMin,
    ) -> AccessorData:
        """
        Convert parameters to an AccessorData instance for use in PID controller.

        :param index: The index of the accessor.
        :type index: int
        :param units: The rate units units to be used (default is RateUnits.MlMin).
        :type units: RateUnits, optional
        :return: The AccessorData instance.
        :rtype: AccessorData
        """
        return AccessorData(
            kind=AccessorKind.PeristalicticRate.value,
            units=units.value,
            device_id=self._device_id,
            index=index,
        )
