"""SolenoidValve Module."""
import enum
from typing import List
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.socket_constants import Actions


class SetPositionCommand:
    """
    Represents a command to set the position of a solenoid valve.

    :param position: The position for the solenoid valve.
    :type position: int
    """

    position: int

    def __init__(self, position: int):
        self.position = position

    def to_command(self):
        """
        Converts the set position command to the command value.

        :return: The command value representing the position.
        :rtype: float
        """
        return self.position


class SolenoidValveLiveKeys(enum.Enum):
    position = "p"


class SolenoidValveLive:
    """
    The live representation of a solenoid valve.

    Attributes:
        position (int): The position solenoid valve.
    """

    mapping = {SolenoidValveLiveKeys.position: "position"}

    """
    The live representation of a solenoid valve.

    Attributes:
        position (int): The percentage open of the solenoid valve.
    """

    def __init__(
        self,
        position: int,
    ):
        """
        Initialize a SolenoidValveLive instance.

        Args:
            position (int): The percentage open of the solenoid valve.
        """
        self.position = position

    @classmethod
    def from_live(cls, **data) -> "SolenoidValveLive":
        """
        Create a SolenoidValveLive instance from the provided live data.

        Args:
            data: The live data of the solenoid valve.

        Returns:
            SolenoidValveLive: The created SolenoidValveLive instance.
        """
        return SolenoidValveLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class SolenoidValve(aqueduct.devices.base.obj.Device):
    """
    Class representing a solenoid valve device in the Aqueduct system.
    """

    @property
    def live(self) -> Tuple[SolenoidValveLive]:
        """
        Get the live data of the solenoid valve.

        Returns:
            Tuple[SolenoidValveLive]: The live data of the solenoid valve as a tuple of SolenoidValveLive objects.
        """
        return self.get_live_and_cast(SolenoidValveLive.from_live)

    def set_position(
        self,
        commands: List[Union[SetPositionCommand, None]],
        record: Union[bool, None] = None,
    ) -> dict:
        """
        Command to set the position of one or more solenoid valve inputs.

        :param commands: List[Union[SetPositionCommand, None]]
        :param record: Whether to record the command (default: None)

        :return: None
        """
        commands = self.map_commands(commands)
        payload = self.to_payload(
            Actions.SetValvePosition, {"commands": commands}, record
        )
        self.send_command(payload)

    def set_command(
        self,
        commands: List[Union[SetPositionCommand, None]],
        index: int,
        command: SetPositionCommand,
    ):
        """
        Helper method to set a solenoid valve command at a specific index.

        :param commands: List[Union[SetPositionCommand, None]]
        :param index: Index of the command
        :param command: SetPositionCommand object

        :return: None
        """
        if index < len(commands):
            commands[index] = command
        else:
            raise Warning("SolenoidValve: command index larger than device size!")

    @staticmethod
    def make_set_position_command(position: float) -> SetPositionCommand:
        """
        Helper method to create a SetPositionCommand object.

        :param position: Position value

        :return: SetPositionCommand object
        """
        return SetPositionCommand(position=position)

    def get_position(self) -> Tuple[float]:
        """
        Get the int of the solenoid valve.

        :return: Tuple of int values
        """
        return self.extract_live_as_tuple(SolenoidValveLiveKeys.position.value)
