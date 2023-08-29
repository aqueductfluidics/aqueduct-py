"""Device object base class."""
from __future__ import annotations

import enum
import json
import socket
import threading
import time
from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import TypeVar

from aqueduct.core.socket_constants import Actions
from aqueduct.core.socket_constants import Events
from aqueduct.core.socket_constants import SOCKET_DELAY_S
from aqueduct.core.socket_constants import SOCKET_TX_ATTEMPTS
from aqueduct.core.socket_constants import SocketCommands
from aqueduct.core.utils import send_and_wait_for_rx


# pylint: disable=invalid-name
class DeviceKeys(enum.Enum):
    """The keys to extract data from the Device."""

    Live = "live"
    Stat = "stat"
    Config = "config"
    Base = "base"


# pylint: disable=invalid-name
class DeviceBaseKeys(enum.Enum):
    """The keys to extract data from the Device Base."""

    DeviceId = "device_id"
    UserId = "user_id"
    Type = "type"
    Name = "name"
    Interface = "interface"


# pylint: disable=invalid-name
class DeviceConfigKeys(enum.Enum):
    """The keys to extract data from the Device Config."""

    Type = "type"
    Config = "config"


# pylint: disable=invalid-name
class DeviceConfigInnerKeys(enum.Enum):
    """The keys to extract data from the Device Config inner data structure."""

    Data = "data"
    Protocol = "protocol"


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
    def to_command(self) -> tuple:
        pass


class CommandPayload:
    """Payload genertor for Device Actions."""

    user_id: str | int
    device_id: int
    action: Actions
    command: dict
    record: bool | None

    def __init__(
        self,
        user_id: str | int,
        device_id: int,
        action: Actions,
        command: dict,
        record: bool | None,
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


T = TypeVar("T")


class Config(ABC):
    """
    Abstract base class for configuration objects.

    Attributes:
        data (List[T]): The configuration data.
        protocol (int): The protocol value.
    """

    def __init__(self, data: list[T], protocol: int):
        """
        Initialize a Config object.

        Args:
            data (List[T]): The configuration data.
            protocol (int): The protocol value.
        """
        self.data = data
        self.protocol = protocol

    @abstractmethod
    def get_data(self) -> list[T]:
        """
        Get the configuration data.

        Returns:
            List[T]: The configuration data.
        """

    @abstractmethod
    def get_protocol(self) -> int:
        """
        Get the protocol value.

        Returns:
            int: The protocol value.
        """


class DeviceConfig(ABC):
    """
    Abstract base class for device configuration objects.

    Attributes:
        config (Config): The configuration object.
        device_type (str): The type of the device.
    """

    def __init__(self, config: Config, type: str):  # pylint: disable=redefined-builtin
        """
        Initialize a DeviceConfig object.

        Args:
            config (Config): The configuration object.
            device_type (str): The type of the device.
        """
        self.config = config
        self.device_type = type

    @abstractmethod
    def get_config(self) -> Config:
        """
        Get the configuration object.

        Returns:
            Config: The configuration object.
        """

    @abstractmethod
    def get_type(self) -> str:
        """
        Get the type of the device.

        Returns:
            str: The type of the device.
        """


class Device:
    """
    Devices are instantiated in Recipes and contain the attributes necessary
    to control execution between the device worker and the main recipe thread.
    """

    def __init__(self, sock: socket.socket, socket_lock: threading.Lock, **kwargs):
        self._socket: socket.socket = sock
        self._socket_lock: threading.Lock = socket_lock

        self._device_id: int = kwargs.get(DeviceKeys.Base.value).get(
            DeviceBaseKeys.DeviceId.value
        )
        self._user_id: str = kwargs.get(DeviceKeys.Base.value).get(
            DeviceBaseKeys.UserId.value
        )
        self._type: str = kwargs.get(DeviceKeys.Base.value).get(
            DeviceBaseKeys.Type.value
        )
        self._name: str = kwargs.get(DeviceKeys.Base.value).get(
            DeviceBaseKeys.Name.value
        )
        self._interface: Interface = kwargs.get(DeviceKeys.Base.value).get(
            DeviceBaseKeys.Interface.value
        )

        self._len: int = len(kwargs.get(DeviceKeys.Live.value))

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

    def map_commands(self, commands: list[Command | None]) -> list:
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
        commands: list[Command | None],
        index: int,
        command: Command,
    ):
        """Helper method set an individual command in a List of `Command`s.

        :return: None
        """
        if index < len(commands):
            commands[index] = command
        else:
            raise Warning("SetCommand error: command index larger than device size!")

    def to_payload(
        self, action: Actions, command: dict, record: bool | None = None
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

    def send_command(self, payload: dict | CommandPayload):
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

    def make_commands(self) -> list[None]:
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
                    data = self._socket.recv(4096 * 8)
                j = json.loads(data)
                if j[0] == Events.GET_DEVICE.value:
                    data = json.loads(j[1]).get("device")
                    base = data.get(DeviceKeys.Base.value)
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
                        return data.get(DeviceKeys.Live.value)
            except (json.decoder.JSONDecodeError, socket.timeout) as _err:
                continue
            i += 1

    T = TypeVar("T")

    def get_live_and_cast(self, cast: Callable) -> tuple:
        """
        Get the live data and cast it using the provided casting function.

        :param cast: The casting function to apply to each live data entry.
        :type cast: Callable
        :return: The casted live data as a tuple.
        :rtype: tuple
        """
        live = []
        for i in self.get_live():
            live.append(cast(**i))
        return tuple(live)

    def get_stat_and_cast(self, cast: Callable) -> tuple:
        """
        Get the stat data and cast it using the provided casting function.

        :param cast: The casting function to apply to each stat data entry.
        :type cast: Callable
        :return: The casted stat data as a tuple.
        :rtype: tuple
        """
        stat = []
        v = self.get()
        for i in v.get(DeviceKeys.Stat.value):
            stat.append(cast(**i))
        return tuple(stat)

    def get_config_and_cast(self, cast: Callable) -> tuple:
        """
        Get the config data and cast it using the provided casting function.

        :param cast: The casting function to apply to each config data entry.
        :type cast: Callable
        :return: The casted config data as a tuple.
        :rtype: tuple
        """
        val = self.get_config()
        return cast(val)

    def get_config(self) -> Config:
        """
        Get the config data.

        :return: The casted config data as a tuple.
        :rtype: tuple
        """
        v = self.get()
        v = v.get(DeviceKeys.Config.value)
        return self.extract_config(v)

    def extract_config(self, data):
        """
        Recursively extract the configuration data from a nested dictionary.

        Args:
            data (dict): The dictionary to extract the configuration data from.

        Returns:
            dict or None: The extracted configuration data if found, or None if not found.
        """
        if isinstance(data, dict):
            if (
                DeviceConfigKeys.Config.value in data
                and DeviceConfigKeys.Type.value in data
            ):
                config_data = self.extract_config_data(
                    data[DeviceConfigKeys.Config.value]
                )
                if config_data is not None:
                    return data
            for value in data.values():
                config_data = self.extract_config(value)
                if config_data:
                    return config_data
        return None

    def extract_config_data(self, data):
        """
        Recursively extract the configuration data from a nested dictionary.

        Args:
            data (dict): The dictionary to extract the configuration data from.

        Returns:
            dict or None: The extracted configuration data if found, or None if not found.
        """
        if isinstance(data, dict):
            if (
                DeviceConfigInnerKeys.Data.value in data
                and DeviceConfigInnerKeys.Protocol.value in data
            ):
                return data
        return None

    def extract_live_as_tuple(
        self, key: str, cast: Callable[[str], T] = None
    ) -> tuple[T]:
        """
        Extracts a specific key from the live data and returns it as a tuple.

        :param key: The key to extract from the live data.
        :type key: str
        :param cast: Optional type to cast the extracted values.
        :type cast: type, optional
        :return: The extracted values as a tuple.
        :rtype: tuple
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            value = ipt.get(key)
            if cast is not None:
                value = cast(value)
            values.append(value)
        return tuple(values)

    def extract_live_as_tuple_of_tuples(
        self, keys: tuple[str], cast: Callable[[str], T] = None
    ) -> tuple[tuple[T]]:
        """
        Extracts multiple keys from the live data and returns them as a tuple of tuples.

        :param keys: The keys to extract from the live data.
        :type keys: Tuple[str]
        :param cast: Optional lambda function to cast the extracted values.
        :type cast: Callable[[str], T], optional
        :return: The extracted values as a tuple of tuples.
        :rtype: Tuple[Tuple[T]]
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            extracted_values = []
            for key in keys:
                value = ipt.get(key)
                if cast is not None:
                    value = cast(value)
                extracted_values.append(value)
            values.append(tuple(extracted_values))
        return tuple(values)

    def update_record(self, record: bool):
        """
        Updates the record status of the device.

        :param record: The record status.
        :type record: bool
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

    def _set_sim_data(
        self,
        values: list[float | None] | tuple | None,
        roc: list[float | None] | tuple | None,
        noise: list[float | None] | tuple | None,
        scale: float = 1.0,
        conversion_func: Callable[[float], float] | None = None,
    ):
        """
        Sets the simulated data for the device.

        :param values: The simulated values.
        :type values: list[float | None] | tuple | None
        :param roc: The rates of change for the simulated values.
        :type roc: list[float | None] | tuple | None
        :param noise: The noise values for the simulated data.
        :type noise: list[float | None] | tuple | None
        :param conversion_func: Optional conversion function to apply to the values. Default is None.
        :type conversion_func: Callable[[float], float], optional
        :param scale: Optional scaling factor for unit conversion. Default is 1.0.
        :type scale: float, optional
        :raises Warning: If the device does not have simulated values.
        """
        if self.has_sim_values:
            v_t = []
            for i in range(0, self.len):
                value = (
                    values[i]
                    if values and i < len(values) and values[i] is not None
                    else None
                )
                roc_value = (
                    roc[i] if roc and i < len(roc) and roc[i] is not None else None
                )
                noise_value = (
                    noise[i]
                    if noise and i < len(noise) and noise[i] is not None
                    else None
                )

                if conversion_func is not None:
                    value = (
                        conversion_func(value * scale) if value is not None else None
                    )
                    roc_value = (
                        conversion_func(roc_value * scale)
                        if roc_value is not None
                        else None
                    )
                    noise_value = (
                        conversion_func(noise_value * scale)
                        if noise_value is not None
                        else None
                    )
                else:
                    value = value * scale if value is not None else None
                    roc_value = roc_value * scale if roc_value is not None else None
                    noise_value = (
                        noise_value * scale if noise_value is not None else None
                    )

                v_t.append((value, roc_value, noise_value))

            payload = self.to_payload(Actions.SetSimValues, v_t, None)
            self.send_command(payload)

        else:
            raise Warning(f"{self.name} does not have simulated values.")

    def _set_sim_values(self, values: list[float | None] | tuple, scale: float = 1.0):
        """
        Sets the simulated values for the device.

        :param values: The simulated values.
        :type values: list[float | None] | tuple
        :param scale: Optional scaling factor for unit conversion. Default is 1.0.
        :type scale: float, optional
        :raises Warning: If the device does not have simulated values.
        """
        self._set_sim_data(values=values, roc=None, noise=None, scale=scale)

    def _set_sim_rates_of_change(
        self, roc: list[float | None] | tuple, scale: float = 1.0
    ):
        """
        Sets the rates of change for the simulated values.

        :param roc: The rates of change for the simulated values.
        :type roc: list[float | None] | tuple
        :param scale: Optional scaling factor for unit conversion. Default is 1.0.
        :type scale: float, optional
        :raises Warning: If the device does not have simulated values.
        """
        self._set_sim_data(values=None, roc=roc, noise=None, scale=scale)

    def _set_sim_noise(self, noise: list[float | None] | tuple, scale: float = 1.0):
        """
        Sets the noise values for the simulated data.

        :param noise: The noise values for the simulated data.
        :type noise: list[float | None] | tuple
        :param scale: Optional scaling factor for unit conversion. Default is 1.0.
        :type scale: float, optional
        :raises Warning: If the device does not have simulated values.
        """
        self._set_sim_data(values=None, roc=None, noise=noise, scale=scale)
