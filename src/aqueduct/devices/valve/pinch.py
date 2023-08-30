"""PinchValve Module."""
import enum
from typing import List
from typing import Tuple
from typing import Union

import aqueduct.devices.base.obj
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import AccessorKind
from aqueduct.core.socket_constants import Actions


class SetPositionCommand:
    """
    Represents a command to set the position of a pinch valve.

    :param pct_open: The percentage open value for the pinch valve.
    :type pct_open: float
    """

    pct_open: float

    def __init__(self, pct_open: float):
        self.pct_open = pct_open

    def to_command(self):
        """
        Converts the set position command to the command value.

        :return: The command value representing the percentage open.
        :rtype: float
        """
        return self.pct_open


class PinchValveLiveKeys(enum.Enum):
    pct_open = "p"


class PinchValveLive:
    """
    The live representation of a pinch valve.

    Attributes:
        pct_open (float): The percentage open of the pinch valve, ranging from 0.0 to 1.0.
    """

    mapping = {PinchValveLiveKeys.pct_open: "pct_open"}

    """
    The live representation of a pinch valve.

    Attributes:
        pct_open (float): The percentage open of the pinch valve, ranging from 0.0 to 1.0.
    """

    def __init__(
        self,
        pct_open: float,
    ):
        """
        Initialize a PinchValveLive instance.

        Args:
            pct_open (float): The percentage open of the pinch valve.
        """
        self.pct_open = pct_open

    @classmethod
    def from_live(cls, **data) -> "PinchValveLive":
        """
        Create a PinchValveLive instance from the provided live data.

        Args:
            data: The live data of the pinch valve.

        Returns:
            PinchValveLive: The created PinchValveLive instance.
        """
        return PinchValveLive(
            **{attr_name: data[key.value] for key, attr_name in cls.mapping.items()}
        )


class PinchValve(aqueduct.devices.base.obj.Device):
    """
    Class representing a pinch valve device in the Aqueduct system.
    """

    @property
    def live(self) -> Tuple[PinchValveLive]:
        """
        Get the live data of the pinch valve.

        Returns:
            Tuple[PinchValveLive]: The live data of the pinch valve as a tuple of PinchValveLive objects.
        """
        return self.get_live_and_cast(PinchValveLive.from_live)

    def set_position(
        self,
        commands: List[Union[SetPositionCommand, None]],
        record: Union[bool, None] = None,
    ) -> dict:
        """
        Command to set the position of one or more pinch valve inputs.

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
        Helper method to set a pinch valve command at a specific index.

        :param commands: List[Union[SetPositionCommand, None]]
        :param index: Index of the command
        :param command: SetPositionCommand object

        :return: None
        """
        if index < len(commands):
            commands[index] = command
        else:
            raise Warning("PinchValve: command index larger than device size!")

    @staticmethod
    def make_set_position_command(pct_open: float) -> SetPositionCommand:
        """
        Helper method to create a SetPositionCommand object.

        :param pct_open: Percentage open value

        :return: SetPositionCommand object
        """
        return SetPositionCommand(pct_open=pct_open)

    def get_pct_open(self) -> Tuple[float]:
        """
        Get the percentage open values of the pinch valve.

        :return: Tuple of percentage open values
        """
        return self.extract_live_as_tuple(PinchValveLiveKeys.pct_open.value)

    def to_pid_control_output(
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
            kind=AccessorKind.Position.value,
            units=0,
            device_id=self._device_id,
            index=index,
        )
