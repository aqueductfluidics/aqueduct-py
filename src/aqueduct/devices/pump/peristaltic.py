"""PeristalticPump Module."""

import enum
from typing import List, Union, Tuple

from aqueduct.devices.base.obj import Command, Device
from aqueduct.core.socket_constants import Actions


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
        return (
            self.mode,
            self.direction,
            self.rate_units,
            self.rate_value,
            self.finite_value,
            self.finite_units,
        )


class StopCommand(Command):
    stop: int

    def __init__(self, **kwargs):
        self.stop = 0

        for k, v in kwargs.items():
            if k in self.__dict__.keys():
                if v is not None:
                    setattr(self, k, v)

    def to_command(self):
        return self.stop


class ChangeSpeedCommand(Command):
    rate_value: Union[float, int]
    rate_units: RateUnits

    def __init__(self, rate_value: Union[float, int], rate_units: RateUnits):
        self.rate_value = rate_value
        self.rate_units = rate_units

    def to_command(self):
        return self.rate_units, self.rate_value


class PeristalticPump(Device):
    """PeristalticPump class."""

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
            Actions.Start,
            {"commands": commands},
            record
        )
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
        payload = self.to_payload(
            Actions.ChangeSpeed,
            {"commands": commands},
            record
        )
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
        """Helper method to create an instance of a :class:`PumpCommand`.

        A :class:`PumpCommand` is an object with the required fields to set the operation
        parameters for a pump input.

        :return: pump_command
        :rtype: PumpCommand
        """
        return ChangeSpeedCommand(rate_value, rate_units)

    def get_ml_min(self) -> Tuple[float]:
        """
        Get all of the diplacement rate values (in mL/min) for the peristaltic pump.

        :Example: read all pumps:

        .. code-block:: python

            ml_min_values = pump.get_ml_min()
            len(ml_min_values) # == pump.len

        :return: weight values
        :rtype: list
        """
        return self.extract_live_as_tuple("mm")
