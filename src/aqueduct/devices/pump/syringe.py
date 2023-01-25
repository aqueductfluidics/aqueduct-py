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
from typing import List, Union, Tuple

from aqueduct.devices.base.obj import Command, Device
from aqueduct.core.socket_constants import Actions


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


class SyringePumpConfig:
    """A configuration object for a syringe pump."""

    def __init__(self, syringe_diam_mm: float, syringe_length_mm: float, syringe_material: str,
                 syringe_volume_ul: float, valve_configuration: int):
        """
        Initializes a SyringePumpConfig object.

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


class SyringePump(Device):
    """A class representing a syringe pump device.

    This class provides an interface to control a syringe pump device. It inherits from the base `Device` class and defines
    additional constants and methods specific to syringe pumps.

    Args:
        socket: The socket used to communicate with the Aqueduct application server.
        socket_lock: A lock used to synchronize access to the socket.
        **kwargs: Additional keyword arguments to pass to the base `Device` constructor.
    """
    stat: List[SyringePumpConfig]

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.stat = []
        for s in kwargs.get('stat'):
            c = SyringePumpConfig(**s)
            self.stat.append(c)

    STATUS = Status
    MODE = Mode
    RATE_UNITS = RateUnits
    FINITE_UNITS = FiniteUnits

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
        commands = [c.to_command() if c is not None else None for c in commands]

        payload = self.to_payload(
            Actions.SetValvePosition,
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
    def make_stop_command() -> ChangeSpeedCommand:
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

    def get_ul_min(self) -> Tuple[float]:
        """
        Get the current displacement rate, in uL/min, for each pump.

        :Example: read all balances:

        .. code-block:: python

            ul_min = pump.get_ul_min()
            len(ul_min) # == pump.len

        :return: uL/min
        :rtype: Tuple[float]
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            values.append(ipt.get("um"))
        return tuple(values)

    def get_status(self) -> Tuple[Status]:
        """
        Get all of the pump input statuses.

        :Example: read all statuses:

        .. code-block:: python

            status = pump.get_status()
            len(state) # == pump.len
            print(status[2]) # == 

        :return: status
        :rtype: Tuple[Status]
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            s = ipt.get("s")
            values.append(Status(int(s)))
        return tuple(values)

    def get_active(self) -> Tuple[bool]:
        """
        Get all of the pump input statuses.

        :Example: read all statuses:

        .. code-block:: python

            active = pump.get_active()
            len(state) # == pump.len
            print(active[2]) # == 

        :return: active
        :rtype: Tuple[bool]
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            s = ipt.get("s")
            values.append(s in (Status.Infusing, Status.Withdrawing))
        return tuple(values)
