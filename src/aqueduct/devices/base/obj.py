"""Device object base class."""

import json
import threading
import socket
import time
import enum

from typing import Union, List, Tuple
from abc import ABC, abstractmethod

from aqueduct.core.socket_constants import (
    SOCKET_DELAY_S,
    SOCKET_TX_ATTEMPTS,
    SocketCommands,
    Events,
    Actions,
)
from aqueduct.core.utils import send_and_wait_for_rx


# pylint: disable=invalid-name
class Interface(enum.IntEnum):
    """The interface of the Device."""

    Sim = 0
    Can = 1
    Ethernet = 2
    Serial = 3


class Command(ABC):
    """
    Abstract base class for command objects. Subclasses must implement
    the `to_command` method, which converts the object to a tuple suitable
    for transmission to a device.

    :Example:

    A `Command` subclass could be used to represent a start command
    for a pump. The `to_command` method would define the appropriate
    tuple structure to send to the pump:

    .. code-block:: python

        class PumpStartCommand(Command):
            def __init__(self, mode, rate, direction):
                self.mode = mode
                self.rate = rate
                self.direction = direction

            def to_command(self):
                return (self.mode, self.rate, self.direction)

        # Create a new command object and send it to the pump
        c = PumpStartCommand(mode="continuous", rate=2, direction="clockwise")
        pump.set_command(pump.make_commands(), 0, c.to_command())

    :ivar mode: the pump's mode (e.g. "continuous" or "step")
    :vartype mode: str

    :ivar rate: the pump's flow rate in mL/min
    :vartype rate: float

    :ivar direction: the pump's direction (e.g. "clockwise" or "counterclockwise")
    :vartype direction: str
    """
    @abstractmethod
    def to_command(self) -> Tuple:
        pass


class CommandPayload:
    """Payload genertor for Device Actions."""

    user_id: Union[str, int]
    device_id: int
    action: Actions
    command: dict
    record: Union[bool, None]

    def __init__(
        self,
        user_id: Union[str, int],
        device_id: int,
        action: Actions,
        command: dict,
        record: Union[bool, None],
    ):
        self.user_id = user_id
        self.device_id = device_id
        self.action = action
        self.command = command
        self.record = record

    def to_dict(self) -> dict:
        """Generate a dictionary from the `CommandPayload`."""
        if self.record is not None:
            return {
                "user_id": self.user_id,
                "device_id": self.device_id,
                "action": self.action,
                "command": self.command,
                "record": self.record,
            }
        return {
            "user_id": self.user_id,
            "device_id": self.device_id,
            "action": self.action,
            "command": self.command,
        }


class Device:
    """
    Devices are instantiated in Recipes and contain the attributes necessary
    to control execution between the device worker and the main recipe thread.
    """

    def __init__(self, sock: socket.socket, socket_lock: threading.Lock, **kwargs):
        self._socket: socket.socket = sock
        self._socket_lock: threading.Lock = socket_lock
        self._device_id: int = kwargs.get("base").get("device_id")
        self._user_id: str = kwargs.get("base").get("user_id")
        self._type: str = kwargs.get("base").get("type")
        self._name: str = kwargs.get("base").get("name")
        self._interface: Interface = kwargs.get("base").get("interface")
        self._len: int = len(kwargs.get("live"))
        self._command_delay: float = 0.0
        self._has_sim_values: bool = False

        if self.interface == Interface.Sim:
            self._command_delay = 0.0
        else:
            self._command_delay: float = 0.01

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def interface(self) -> Interface:
        """Return the interface the device is connected to."""
        return self._interface

    @property
    def len(self) -> int:
        """Return size of the device (number of nodes)."""
        return self._len

    @property
    def command_delay(self) -> float:
        """Return the command delay (in seconds)."""
        return self._command_delay
    
    @command_delay.setter
    def command_delay(self, value: float):
        """Set the command delay (in seconds)."""
        self._command_delay = value
    
    @property
    def has_sim_values(self) -> float:
        """Return whether the Device has `simmable` values."""
        return self._has_sim_values
    
    @has_sim_values.setter
    def has_sim_values(self, value: bool):
        """Set whether the Device has simulated values."""
        self._has_sim_values = value

    def map_commands(self, commands: List[Union[Command, None]]) -> List:
        """
        Abstract method to return the command as a List of bytes.

        This method must be implemented in all concrete command objects to convert the command to a tuple
        of bytes that can be sent to the device.

        :return: The command as a List of parameters.
        :rtype: List
        """
        commands = [c.to_command() if c is not None else None for c in commands]
        return commands
    
    def set_command(
        self,
        commands: List[Union[Command, None]],
        index: int,
        command: Command,
    ):
        """Helper method set an individual command in a List of `Command`s.

        :return: None
        """
        if index < len(commands):
            commands[index] = command
        else:
            raise Warning(
                "SetCommand error: command index larger than device size!")

    def to_payload(
        self, 
        action: Actions, 
        command: dict, 
        record: Union[bool, None] = None
    ) -> CommandPayload:
        """Generate an `Action` payload."""
        return CommandPayload(self._user_id, self._device_id, action, command, record)

    def generate_action_payload(self) -> dict:
        """Generate the required base keys and values for sending a command to the TCP Socket."""
        return {
            "user_id": self._user_id,
            "device_id": self._device_id,
            "action": None,
        }

    def send_command(self, payload: Union[dict, CommandPayload]):
        """Send a `Command` to the TCP Socket."""
        if isinstance(payload, CommandPayload):
            payload = payload.to_dict()

        message = json.dumps(
            [SocketCommands.SocketMessage.value, [Events.DEVICE_ACTION.value, payload]]
        ).encode()

        return send_and_wait_for_rx(
            message,
            self._socket,
            self._socket_lock,
            Events.DEVICE_ACTION.value,
            SOCKET_TX_ATTEMPTS,
            delay_s=self.command_delay,
        )
    
    def make_commands(self) -> List[None]:
        """Helper method to create an empty list with the length of the Device.

        :return: commands
        :rtype: List[None]
        """
        return self.len * [None]

    def is_for_me(self, base: dict) -> bool:
        """Decide whether a an action payload is intended for this device."""
        return (
            base.get("device_id") == self._device_id
            and base.get("user_id") == self._user_id
        )

    def get(self):
        """Get the device data from the TCP socket."""
        payload = self.generate_action_payload()
        message = json.dumps(
            [SocketCommands.SocketMessage.value, [Events.GET_DEVICE.value, payload]]
        ).encode()
        i = 0
        while i < SOCKET_TX_ATTEMPTS:
            try:
                with self._socket_lock:
                    self._socket.settimeout(0.5)
                    self._socket.send(message)
                    time.sleep(SOCKET_DELAY_S)
                    data = self._socket.recv(1024 * 8)
                j = json.loads(data)
                if j[0] == Events.GET_DEVICE.value:
                    data = json.loads(j[1]).get("device")
                    base = data.get("base")
                    if self.is_for_me(base):
                        return data
            except (json.decoder.JSONDecodeError, socket.timeout) as _err:
                continue
            i += 1

    def get_live(self):
        """Get only the live device attributes of the device."""
        payload = self.generate_action_payload()
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.GET_DEVICE_LIVE.value, payload],
            ]
        ).encode()
        i = 0
        while i < SOCKET_TX_ATTEMPTS:
            try:
                with self._socket_lock:
                    self._socket.settimeout(0.5)
                    self._socket.send(message)
                    time.sleep(SOCKET_DELAY_S)
                    data = self._socket.recv(1024 * 8)
                j = json.loads(data)
                if j[0] == Events.GET_DEVICE_LIVE.value:
                    data = json.loads(j[1])
                    if self.is_for_me(data):
                        return data.get("live")
            except (json.decoder.JSONDecodeError, socket.timeout) as _err:
                continue
            i += 1

    def update_record(self, record: bool):
        """Toggle whether the PH3 device is recording.

        :Example: Start recording data for the PH3 device named PH3SIM:

        .. code-block:: python

            PH3SIM.update_record(True)

        :return: command dictionary
        :rtype: dict
        """
        payload = self.to_payload(Actions.UpdateRecord, None, record)
        self.send_command(payload)

    def clear_recorded(self):
        """Clear the recorded data for the device. The recordable data includes"""
        payload = self.generate_action_payload()

        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.CLEAR_DEVICE_RECORDABLE.value, payload],
            ]
        ).encode()

        return send_and_wait_for_rx(
            message,
            self._socket,
            self._socket_lock,
            Events.DEVICE_ACTION.value,
            SOCKET_TX_ATTEMPTS,
            delay_s=self.command_delay,
        )

    def set_sim_data(
        self,
        values: Union[tuple, list],
        roc: Union[tuple, list],
        noise: Union[tuple, list],
    ):
        if self.has_sim_values:
            v_t = []
            for i in range(0, self.len):
                try:
                    v_v = values[i]
                except IndexError:
                    v_v = None
                try:
                    r_c = roc[i]
                except IndexError:
                    r_c = None
                try:
                    n_v = noise[i]
                except IndexError:
                    n_v = None
                v_t.append((v_v, r_c, n_v))

            payload = self.to_payload(Actions.SetSimValues, v_t, None)
            self.send_command(payload)
        
        else:
            raise Warning(f"{self.name} does not have simulated values.")

    def set_sim_values(self, values: Union[tuple, list]):
        if self.has_sim_values:
            v_t = []
            for i in range(0, self.len):
                try:
                    v_v = values[i]
                except IndexError:
                    v_v = None
                v_t.append((v_v, None, None))

            payload = self.to_payload(Actions.SetSimValues, v_t, None)
            self.send_command(payload)
        
        else:
            raise Warning(f"{self.name} does not have simulated values.")

    def set_sim_rates_of_change(self, roc: Union[tuple, list]):
        if self.has_sim_values:
            v_t = []
            for i in range(0,self.len):
                try:
                    r_c = roc[i]
                except IndexError:
                    r_c = None
                v_t.append((None, r_c, None))

            payload = self.to_payload(Actions.SetSimValues, v_t, None)
            self.send_command(payload)
        
        else:
            raise Warning(f"{self.name} does not have simulated values.")

    def set_sim_noise(self, noise: Union[tuple, list]):
        if self.has_sim_values:
            v_t = []
            for i in range(0,self.len):
                try:
                    n_v = noise[i]
                except IndexError:
                    n_v = None
                v_t.append((None, None, n_v))

            payload = self.to_payload(Actions.SetSimValues, v_t, None)
            self.send_command(payload)

        else:
            raise Warning(f"{self.name} does not have simulated values.")