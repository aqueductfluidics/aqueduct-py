# pylint: disable=line-too-long
"""
SyringePump Module.

Classes:
    SyringePump: A class for controlling a syringe pump.
    Mode: An enumeration representing the operational mode of a syringe pump (continuous or finite).
    Status: An enumeration representing the status of a syringe pump (stopped, infusing, withdrawing, or paused).
    RateUnits: An enumeration representing the units used when setting the speed of a syringe pump.
    FiniteUnits: An enumeration representing the units used when setting the volume for a finite mode operation.
    StartCommand: A class representing a command to start one or more syringe pump inputs in either continuous or finite mode.
    StopCommand: A class representing a command to stop one or more syringe pump inputs.
    ChangeSpeedCommand: A class representing a command to change the speed of one or more syringe pump inputs.
    SetRotaryValveCommand: A class representing a command to set the rotary valves of one or more syringe pump inputs.

Methods:
    start(commands: List[Union[StartCommand, None]], record: Union[bool, None] = None) -> dict:
        Command to start one or more pump inputs in either finite or continuous mode.
    change_speed(commands: List[Union[ChangeSpeedCommand, None]], record: Union[bool, None] = None) -> dict:
        Command to change the speed of one or more pump inputs.
    stop(commands: List[Union[ChangeSpeedCommand, None]] = None) -> dict:
        Stop one or more pump inputs.
    set_valves(commands: List[Union[SetRotaryValveCommand, None]] = None) -> dict:
        Set the rotary valves of one or more pumps.
    set_command(commands: List[Union[StartCommand, StopCommand, ChangeSpeedCommand, None]], index: int,
                command: Union[StartCommand, StopCommand, ChangeSpeedCommand]):
        Helper method to create an instance of a `PumpCommand`.
    make_start_command(mode: Mode, direction: Status, rate_value: Union[float, int], rate_units: RateUnits,
                       finite_value: Union[float, int, None] = None, finite_units: Union[FiniteUnits, None] = None) -> StartCommand:
        Helper method to create an instance of a `StartCommand`.
    make_stop_command() -> ChangeSpeedCommand:
        Helper method to create an instance of a `StopCommand`.
    make_change_speed_command(rate_value: Union[float, int], rate_units: RateUnits) -> ChangeSpeedCommand:
        Helper method to create an instance of a `ChangeSpeedCommand`.
    make_set_valve_command(port: int, direction: Union[int, None] = None) -> SetRotaryValveCommand:
        Helper method to create an instance of a `SetRotaryValveCommand`.
    get_ul_min() -> Tuple[float]:
        Get all of the weight readings from a Balance device.
    get_status() -> Tuple[bool]:
        Get all of the pump input statuses.
"""
# pylint: disable=too-few-public-methods
import enum
from typing import List
from typing import Tuple
from typing import Union

from aqueduct.core.socket_constants import Actions
from aqueduct.devices.base.obj import Command
from aqueduct.devices.base.obj import Device
from aqueduct.devices.base.obj import DeviceConfigInnerKeys
from aqueduct.devices.base.obj import DeviceConfigKeys

from .types import Config
from .types import tricontinent

# pylint: disable=invalid-name


class Mode(enum.IntEnum):
    """Operational Mode of the `SyringePump`. Use this value to set the operation to continuous or finite."""

    Continuous = 0
    Finite = 1


# pylint: disable=invalid-name
class Status(enum.IntEnum):
    """Status of the `SyringePump`. Use this value to set a direction."""

    Stopped = 0
    Infusing = 1
    Withdrawing = 2
    Paused = 3

    def reverse(self) -> "Status":
        """Returns the opposite direction of the current `Status`.

        If the current `Status` is Infusing, it returns Withdrawing.
        If the current `Status` is Withdrawing, it returns Infusing.
        For all other values, it returns the current `Status`.

        Returns:
            Status: The opposite direction of the current `Status`.
        """
        if self == Status.Infusing:
            return Status.Withdrawing
        elif self == Status.Withdrawing:
            return Status.Infusing
        else:
            return self


# pylint: disable=invalid-name
class RateUnits(enum.IntEnum):
    """Rate units used when starting or changing the speed of a `SyringePump`."""

    UlMin = 0
    UlHr = 1
    MlMin = 2
    MlHr = 3


# pylint: disable=invalid-name
class FiniteUnits(enum.IntEnum):
    """Units used when starting the pump for a `finite` mode operation."""

    Ul = 0
    Ml = 1


# pylint: disable=invalid-name
class ResolutionMode(enum.IntEnum):
    """Units used when setting the plunger resolution mode."""

    N0 = 0
    N1 = 1
    N2 = 2


class StartCommand(Command):
    """A command to start a pump input.

    Args:
        mode (Mode): The operational mode of the SyringePump.
        direction (Status): The direction to set for the pump input.
        rate_value (Union[float, int]): The speed at which to run the pump input.
        rate_units (RateUnits): The rate units used for the pump input.
        finite_value (Union[float, int, None], optional): The finite value to use for finite mode operation. Defaults to None.
        finite_units (Union[FiniteUnits, None], optional): The units used for finite mode operation. Defaults to None.
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
        """Initialize the StartCommand instance."""
        self.mode = mode
        self.direction = direction
        self.rate_value = rate_value
        self.rate_units = rate_units
        self.finite_value = finite_value
        self.finite_units = finite_units

    def to_command(self):
        """Convert the StartCommand instance to a command tuple."""
        return (
            self.mode,
            self.direction,
            self.rate_units,
            self.rate_value,
            self.finite_value,
            self.finite_units,
        )


class StopCommand(Command):
    """A command to stop the SyringePump input.

    Args:
        stop (int): A flag to indicate whether to stop the input.

    Attributes:
        stop (int): A flag to indicate whether to stop the input.
    """

    stop: int

    def __init__(self, **kwargs):
        """Initialize the StopCommand instance."""
        self.stop = 0

        for k, v in kwargs.items():
            if k in self.__dict__.keys():
                if v is not None:
                    setattr(self, k, v)

    def to_command(self):
        """Convert the StopCommand instance to a command tuple."""
        return self.stop


class ChangeSpeedCommand(Command):
    """A command to change the speed of a pump input.

    Args:
        rate_value (Union[float, int]): The new speed value for the pump input.
        rate_units (RateUnits): The rate units used for the pump input.
    """

    rate_value: Union[float, int]
    rate_units: RateUnits

    def __init__(self, rate_value: Union[float, int], rate_units: RateUnits):
        """Initialize the ChangeSpeedCommand instance."""
        self.rate_value = rate_value
        self.rate_units = rate_units

    def to_command(self):
        """Convert the ChangeSpeedCommand instance to a command tuple."""
        return self.rate_units, self.rate_value


class SetRotaryValveCommand(Command):
    """A command to set the position and direction of a rotary valve.

    Args:
        port (int): The port to which the rotary valve is connected.
        direction (Union[int, None]): The direction to rotate the valve (if any). Defaults to None (shortest direction)

    Attributes:
        port (int): The port to which the rotary valve is connected.
        direction (Union[int, None]): The direction to set the rotary valve. None for no movement, 1 or -1 for movement.
    """

    port: int
    direction: Union[int, None]

    def __init__(self, port: int, direction: Union[int, None]):
        """Initialize the SetRotaryValveCommand instance.

        Args:
            port (int): The port to which the rotary valve is connected.
            direction (Union[int, None]): The direction to set the rotary valve. None for no movement, 1 or -1 for movement.
        """
        self.port = port
        self.direction = direction

    def to_command(self):
        """Convert the SetRotaryValveCommand instance to a command tuple.

        Returns:
            Tuple[int, Union[int, None]]: The port and direction to set the rotary valve.
        """
        return self.port, self.direction


class SetPlungerResolutionCommand(Command):
    """A command to set the plunger resolution mode of a syringe pump.

    Args:
        mode (ResolutionMode): Plunger resolution mode for the command.

    Attributes:
        mode (ResolutionMode): Plunger resolution mode for the command.
    """

    mode: ResolutionMode

    def __init__(self, mode: ResolutionMode):
        """Initialize the SetPlungerResolutionCommand instance.

        Args:
            mode (ResolutionMode): Plunger resolution mode for the command.
        """
        self.mode = mode

    def to_command(self):
        """Convert the SetPlungerResolutionCommand instance to a command tuple.

        Returns:
            int: The plunger resolution mode.
        """
        return self.mode.value


class SyringePumpStat:
    """A stat object for a syringe pump."""

    def __init__(
        self,
        syringe_diam_mm: float,
        syringe_length_mm: float,
        syringe_material: str,
        syringe_volume_ul: float,
        valve_configuration: int,
    ):
        """
        Initializes a SyringePumpStat object.

        Args:
            syringe_diam_mm (float): The diameter of the syringe in millimeters.
            syringe_length_mm (float): The length of the syringe in millimeters.
            syringe_material (str): The material of the syringe.
            syringe_volume_ul (float): The volume of the syringe in microliters.
            valve_configuration (int): The valve configuration to use for the syringe pump.
        """
        self.syringe_diam_mm = syringe_diam_mm
        self.syringe_length_mm = syringe_length_mm
        self.syringe_material = syringe_material
        self.syringe_volume_ul = syringe_volume_ul
        self.valve_configuration = valve_configuration

    @classmethod
    def from_stat(cls, **data) -> "SyringePumpStat":
        """
        Create a SyringePumpConfig object from stat data.

        Args:
            **data: Keyword arguments representing the stat data.
        Returns:
            SyringePumpConfig: The created SyringePumpConfig object.
        """
        return SyringePumpStat(**data)


class SyringePumpLiveKeys(enum.Enum):
    """
    Enum representing the keys used in SyringePumpLive serialization/deserialization.
    """

    status = "s"
    mode = "m"
    ul_min = "um"
    finite_value = "fv"
    finite_units = "fu"
    finite_ul_target = "ft"
    finite_ul_infused = "fi"
    finite_ul_withdrawn = "fw"
    position = "p"
    position_target = "pt"
    valve_position = "v"
    plunger_mode = "pm"


class SyringePumpLive:
    """
    The live representation of a syringe pump.
    """

    mapping = {
        SyringePumpLiveKeys.status: "status",
        SyringePumpLiveKeys.mode: "mode",
        SyringePumpLiveKeys.ul_min: "ul_min",
        SyringePumpLiveKeys.finite_value: "finite_value",
        SyringePumpLiveKeys.finite_units: "finite_units",
        SyringePumpLiveKeys.finite_ul_target: "finite_ul_target",
        SyringePumpLiveKeys.finite_ul_infused: "finite_ul_infused",
        SyringePumpLiveKeys.finite_ul_withdrawn: "finite_ul_withdrawn",
        SyringePumpLiveKeys.position: "position",
        SyringePumpLiveKeys.position_target: "position_target",
        SyringePumpLiveKeys.valve_position: "valve_position",
        SyringePumpLiveKeys.plunger_mode: "plunger_mode",
    }

    """
    The live representation of a syringe pump.

    Attributes:
        status (Status): The status of the syringe pump.
        mode (Mode): The operational mode of the syringe pump.
        ul_min (float): The current infusion or withdrawal rate of the pump, in uL/min.
        finite_value (float): The target volume to dispense or withdraw when operating in Finite mode.
        finite_units (FiniteUnits): The units of the target volume in Finite mode.
        finite_ul_target (float): The target volume to dispense or withdraw in uL when operating in Finite mode.
        finite_ul_infused (float): The infused volume in uL when operating in Finite mode.
        finite_ul_withdrawn (float): The withdrawn volume in uL when operating in Finite mode.
        position (float): The plunger position of the syringe pump from 0.0 to 1.0.
        position_target (float): The target plunger position of the syringe pump from 0.0 to 1.0.
        valve_position (int): The valve position of the syringe pump.
        plunger_mode (int): The plunger positioning mode of the syringe pump.
    """

    def __init__(
        self,
        status: Status,
        mode: Mode,
        ul_min: float,
        finite_value: float,
        finite_units: FiniteUnits,
        finite_ul_target: float,
        finite_ul_infused: float,
        finite_ul_withdrawn: float,
        position: float,
        position_target: float,
        valve_position: int,
        plunger_mode: int,
    ):
        self.status = status
        self.mode = mode
        self.ul_min = ul_min
        self.finite_value = finite_value
        self.finite_units = finite_units
        self.finite_ul_target = finite_ul_target
        self.finite_ul_infused = finite_ul_infused
        self.finite_ul_withdrawn = finite_ul_withdrawn
        self.position = position
        self.position_target = position_target
        self.valve_position = valve_position
        self.plunger_mode = plunger_mode

    @classmethod
    def from_live(cls, **data) -> "SyringePumpLive":
        """
        Create a SyringePumpLive object from live data.

        Args:
            **data: Key-value pairs representing the live data.

        Returns:
            SyringePumpLive: The created SyringePumpLive object.
        """
        return SyringePumpLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class SyringePump(Device):
    """A class representing a syringe pump device.

    This class provides an interface to control a syringe pump device. It inherits from the base `Device` class and defines
    additional constants and methods specific to syringe pumps.

    Args:
        socket: The socket used to communicate with the Aqueduct application server.
        socket_lock: A lock used to synchronize access to the socket.
        **kwargs: Additional keyword arguments to pass to the base `Device` constructor.
    """

    STATUS = Status
    MODE = Mode
    RATE_UNITS = RateUnits
    FINITE_UNITS = FiniteUnits

    @property
    def live(self) -> Tuple[SyringePumpLive]:
        """
        Get the live data of the syringe pump.

        Returns:
            Tuple[SyringePumpLive]: The live data of the syringe pump as a tuple of SyringePumpLive objects.
        """
        return self.get_live_and_cast(SyringePumpLive.from_live)

    @property
    def stat(self) -> Tuple[SyringePumpStat]:
        """
        Get the stat data of the syringe pump.

        Returns:
            Tuple[SyringePumpStat]: The stat data of the syringe pump as a tuple of SyringePumpStat objects.
        """
        return self.get_stat_and_cast(SyringePumpStat.from_stat)

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
                and data.get(DeviceConfigKeys.Type.value) == Config.TriContinent.value
            ):
                configs = []
                for _i, d in enumerate(
                    data.get(DeviceConfigKeys.Config.value).get(
                        DeviceConfigInnerKeys.Data.value
                    )
                ):
                    configs.append(tricontinent.TriContinentConfig(**d))
                data[DeviceConfigKeys.Config.value][
                    DeviceConfigInnerKeys.Data.value
                ] = configs
                return data
            else:
                return data

        return self.get_config_and_cast(cast_config)

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
        payload = self.to_payload(Actions.Start, {"commands": commands}, record)
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
        payload = self.to_payload(Actions.ChangeSpeed, {"commands": commands}, record)
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

    def set_valves(
        self,
        commands: List[Union[SetRotaryValveCommand, None]] = None,
    ) -> dict:
        """Set the rotary valves of one or more pumps.

        .. code-block:: python

            commands = pump.make_commands()
            command = pump.make_set_valve_command(5)
            pump.set_command(commands, 0, command)
            pump.set_valves(commands)

        :param commands: List[Union[ChangeSpeedCommand, None]]

        :param commands:

        :return: None
        :rtype: None
        """
        commands = self.map_commands(commands)

        payload = self.to_payload(
            Actions.SetValvePosition,
            {"commands": commands},
        )
        self.send_command(payload)

    def set_plunger_mode(
        self,
        commands: Union[List[Union[SetPlungerResolutionCommand, None]], None] = None,
    ) -> dict:
        """Set the plunger mode for one or more pump inputs.

        :param commands: List of plunger mode commands for each pump input.
        :type commands: Union[List[Union[SetPlungerResolutionCommand, None]], None]

        :return: The response payload.
        :rtype: dict
        """
        commands = self.map_commands(commands)

        payload = self.to_payload(
            Actions.SetPlunger,
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
        """Helper method to create an instance of a :class:`ChangeSpeedCommand`.

        A :class:`PumpCommand` is an object with the required fields to set the operation
        parameters for a pump input.

        :return: pump_command
        :rtype: PumpCommand
        """
        return ChangeSpeedCommand(rate_value, rate_units)

    @staticmethod
    def make_set_valve_command(
        port: int, direction: Union[int, None] = None
    ) -> SetRotaryValveCommand:
        """Helper method to create an instance of a :class:`PumpCommand`.

        A :class:`PumpCommand` is an object with the required fields to set the operation
        parameters for a pump input.

        :return: pump_command
        :rtype: PumpCommand
        """
        return SetRotaryValveCommand(port, direction)

    @staticmethod
    def make_set_plunger_mode_command(
        mode: ResolutionMode,
    ) -> SetPlungerResolutionCommand:

        return SetPlungerResolutionCommand(mode)

    def get_ul_min(self) -> Tuple[float]:
        """
        Get the current displacement rate, in uL/min, for each pump.

        :return: uL/min
        :rtype: Tuple[float]
        """
        return self.extract_live_as_tuple(SyringePumpLiveKeys.ul_min.value)

    def get_plunger_position(self) -> Tuple[float]:
        """
        Get the current plunger position for each pump.

        The plunger position of the syringe pump, from 0. to 1.

        A value of `0.` indicates that the pump is in the fully infused
        position.

        A value of `1.` indicates that the pump is in the fully
        withdrawn position.

        :return: plunger position
        :rtype: Tuple[float]
        """
        return self.extract_live_as_tuple(SyringePumpLiveKeys.position.value)

    def get_plunger_position_volume(self) -> Tuple[float]:
        """
        Get the current plunger position in uL.

        :return: plunger position
        :rtype: Tuple[float]
        """
        plunger_position = self.get_plunger_position()
        volume = [
            v * self.stat[i].syringe_volume_ul for i, v in enumerate(plunger_position)
        ]
        return tuple(volume)

    def get_status(self) -> Tuple[Status]:
        """
        Get all of the pump input statuses.

        :return: status
        :rtype: Tuple[Status]
        """

        def cast_function(s):
            return Status(int(s))

        return self.extract_live_as_tuple(
            SyringePumpLiveKeys.status.value, cast_function
        )

    def get_active(self) -> Tuple[bool]:
        """
        Get all of the pump input statuses.

        :return: active
        :rtype: Tuple[bool]
        """

        def cast_function(s):
            return s in (Status.Infusing, Status.Withdrawing)

        return self.extract_live_as_tuple(
            SyringePumpLiveKeys.status.value, cast_function
        )

    def get_max_flow_rate_ul_min(self) -> Tuple[float]:
        """
        Get the maximum flow rate in microliters per minute for each pump.

        :return: Tuple of maximum flow rates for each pump.
        :rtype: Tuple[float]
        """

        config = self.get_config()
        values = [1000000.0] * self.len

        if config is None:
            return values

        if config.get(DeviceConfigKeys.Type.value) == Config.TriContinent.value:
            live = self.live
            stat = self.stat

            for i, d in enumerate(
                config.get(DeviceConfigKeys.Config.value).get(
                    DeviceConfigInnerKeys.Data.value
                )
            ):
                pump_series = d.get(
                    tricontinent.TriContinentConfigKeys.PumpSeries.value
                )
                resolution = live[i].plunger_mode
                syringe_volume_ul = stat[i].syringe_volume_ul
                value = tricontinent.max_rate_ul_min(
                    pump_series, resolution, syringe_volume_ul
                )
                if value is not None:
                    values[i] = value

        return tuple(values)

    def get_min_flow_rate_ul_min(self) -> Tuple[float]:
        """
        Get the minimum flow rate in microliters per minute for each pump.

        :return: Tuple of minimum flow rates for each pump.
        :rtype: Tuple[float]
        """

        config = self.get_config()
        values = [0.0] * self.len

        if config is None:
            return values

        if config.get(DeviceConfigKeys.Type.value) == Config.TriContinent.value:
            live = self.live
            stat = self.stat

            for i, d in enumerate(
                config.get(DeviceConfigKeys.Config.value).get(
                    DeviceConfigInnerKeys.Data.value
                )
            ):
                pump_series = d.get(
                    tricontinent.TriContinentConfigKeys.PumpSeries.value
                )
                resolution = live[i].plunger_mode
                syringe_volume_ul = stat[i].syringe_volume_ul

                value = tricontinent.min_rate_ul_min(
                    pump_series, resolution, syringe_volume_ul
                )
                if value is not None:
                    values[i] = value

        return tuple(values)
