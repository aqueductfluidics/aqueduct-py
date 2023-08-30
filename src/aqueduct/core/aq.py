"""
Aqueduct Class Module

The code is a module that defines the Aqueduct class, which is
used to interact with the Aqueduct system for managing experiments.
The class has methods for registering a process with the Aqueduct system,
pausing a recipe, updating process status, and getting setup information.

The class also has an initialization method that starts a helper thread
and registers the process. There is also an InitParams class used for
parsing command line arguments.

The Aqueduct class provides an interface to control devices and data
in the Aqueduct system.

Attributes:
    devices (dict): A dictionary of devices controlled by Aqueduct.
    _socket (socket.socket): A socket object used for communication.
    _socket_lock (threading.Lock): A threading lock object for the socket.
    _helper (AqHelper): An AqHelper object used for communicating with the server.
    _helper_t (threading.Thread): A threading thread object for AqHelper.
    _setpoints (dict): A dictionary of setpoints for the system.
    _recordables (dict): A dictionary of recordables for the system.
    _pid (int): The process ID of the Aqueduct instance.
    _address (str): The IP address of the Aqueduct server.
    _port (int): The port number of the Aqueduct server.
    _debug (bool): Whether debugging is enabled.
    _pause_on_queue (bool): Whether to pause on queue.
    _serial_number (Union[int, None]): The serial number of the Aqueduct instance.

"""
import argparse
import datetime
import json
import os
import socket
import subprocess
import sys
import threading
import time
import typing
import warnings

import psutil
from aqueduct.core.input import Input
from aqueduct.core.input import UserInputTypes
from aqueduct.core.logging import AqLogger
from aqueduct.core.pid import AccessorData
from aqueduct.core.pid import Pid
from aqueduct.core.pid import PidController
from aqueduct.core.prompt import Prompt
from aqueduct.core.recordable import Recordable
from aqueduct.core.setpoint import Setpoint
from aqueduct.core.socket_constants import Events
from aqueduct.core.socket_constants import OK
from aqueduct.core.socket_constants import SOCKET_DELAY_S
from aqueduct.core.socket_constants import SOCKET_TX_ATTEMPTS
from aqueduct.core.socket_constants import SocketCommands
from aqueduct.core.utils import send_and_wait_for_rx
from aqueduct.core.utils import split_packets
from aqueduct.core.utils import string_to_bool
from aqueduct.devices.base.obj import Device
from aqueduct.devices.base.utils import create_device
from aqueduct.devices.base.utils import DeviceTypes


class InitParams:
    """
    A class to hold initialization parameters.

    Attributes:
        user_id (typing.Union[int, str]): user id.
        ip_address (str): IP address.
        port (int): port number.
        init (bool): whether to initialize.
        register_process (bool): whether to register the process with the
            application to enable remote pause/resume of recipe.
    """

    user_id: typing.Union[int, str]
    ip_address: str
    port: int
    init: bool
    register_process: bool

    def __init__(
        self, user_id, ip_address, port, init, register_process: bool = True
    ) -> None:
        """
        Initializes InitParams class.

        Args:
            user_id (typing.Union[int, str]): user id.
            ip_address (str): IP address.
            port (int): port number.
            init (bool): whether to initialize.
            register_process (bool): whether to register the Python process with the
                application to enable remote pause/resume of recipe.
        """
        self.user_id = user_id
        self.ip_address = ip_address
        self.port = port
        self.init = init
        self.register_process = register_process

    @classmethod
    def parse(cls):
        """
        Parses command-line arguments to create an instance of InitParams.

        Returns:
            An instance of InitParams with the parsed arguments.

        Note:
            If any argument is not provided, it defaults to None.
        """

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-u",
            "--user_id",
            type=str,
            help="user_id (either int or 'L')",
            default=None,
        )

        parser.add_argument(
            "-a",
            "--addr",
            type=str,
            help="IP address (no port, like 127.0.0.1)",
            default=None,
        )

        parser.add_argument(
            "-p", "--port", type=int, help="port (like 59000)", default=None
        )

        parser.add_argument(
            "-i",
            "--init",
            type=int,
            help="initialize (1 for true, 0 for false)",
            default=None,
        )

        parser.add_argument(
            "-r",
            "--register",
            type=int,
            help="register process (1 for true, 0 for false)",
            default=1,
        )

        args, _unknown = parser.parse_known_args()

        user_id = args.user_id
        ip_address = args.addr
        port = args.port
        init = bool(args.init)
        register_process = bool(args.register)

        return cls(user_id, ip_address, port, init, register_process)


class Aqueduct:
    """
    Provides an interface to control devices and data in the Aqueduct system.

    Args:
        user_id (typing.Union[None, int, str]): The user ID. If None,
            it will default to the 'AQ_USER_ID' environment variable.
        address (typing.Union[str, None]): The IP address. If None,
            it will default to the 'AQ_TCP_ADDRESS' environment variable or '127.0.0.1'.
        port (typing.Union[int, None]): The port number. If None, it will
            default to the 'AQ_TCP_PORT' environment variable or 59000.
        pause (typing.Union[bool, None]): Whether to pause on queue. If None,
            it will default to the 'AQ_PAUSE_ON_QUEUE' environment variable or True.
        register_process (typing.Union[bool, None]): whether to register the Python process with the
                application to enable remote pause/resume of recipe.

    Attributes:
        devices (dict): A dictionary of devices controlled by Aqueduct.
        _socket (socket.socket): A socket object used for communication.
        _socket_lock (threading.Lock): A threading lock object for the socket.
        _helper (AqHelper): An AqHelper object used for communicating with the server.
        _helper_t (threading.Thread): A threading thread object for AqHelper.
        _setpoints (dict): A dictionary of setpoints for the system.
        _recordables (dict): A dictionary of recordables for the system.
        _logger (AqLogger): A logger object for logging messages to a file.
        _pid (int): The process ID of the Aqueduct instance.
        _address (str): The IP address of the Aqueduct server.
        _port (int): The port number of the Aqueduct server.
        _debug (bool): Whether debugging is enabled.
        _pause_on_queue (bool): Whether to pause on queue.
        _serial_number (Union[int, None]): The serial number of the Aqueduct instance.

    """

    devices: dict

    _socket: socket.socket
    _socket_lock: threading.Lock
    _helper: "AqHelper"
    _helper_t: threading.Thread
    _setpoints: dict
    _recordables: dict
    _logger: AqLogger
    _pid: int
    _address: str
    _port: int
    _debug: bool = False
    _pause_on_queue: bool = False
    _serial_number: typing.Union[int, None] = None
    _application_version: typing.Union[str, None] = None
    _register_process: typing.Union[bool, None] = None

    def __init__(
        self,
        user_id: typing.Union[None, int, str] = None,
        address: typing.Union[str, None] = None,
        port: typing.Union[int, None] = None,
        pause: typing.Union[bool, None] = None,
        register_process: typing.Union[bool, None] = None,
    ):
        """
        Initializes an instance of Aqueduct.

        Args:
            user_id (typing.Union[None, int, str]): The user ID.
            address (typing.Union[str, None]): The IP address.
            port (typing.Union[int, None]): The port number.
            pause (typing.Union[bool, None]): Whether to pause on queue.
        """
        if user_id is None:
            user_id = os.environ.get("AQ_USER_ID", "1")

        if address is None:
            address = os.environ.get("AQ_TCP_ADDRESS", "127.0.0.1")

        if port is None:
            port = int(os.environ.get("AQ_TCP_PORT", 59000))

        if pause is None:
            pause = bool(int(os.environ.get("AQ_PAUSE_ON_QUEUE", 1)))

        if register_process is None:
            register_process = True

        self._user_id = user_id
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_lock = threading.Lock()
        self._socket.connect((address, port))
        self._helper = AqHelper(self, address, port)
        self._logger = AqLogger(None, None)
        self._setpoints = {}
        self._recordables = {}
        self._pid = os.getpid()
        self._address = address
        self._port = port
        self._pause_on_queue = pause
        self._register_process = register_process

        if os.environ.get("AQ_SERIAL_NUMBER") is not None:
            self._serial_number = int(os.environ.get("AQ_SERIAL_NUMBER"))

        self.devices: dict = {}

    @property
    def socket(self):
        """
        Returns the socket object.

        :return: A socket object.
        """
        return self._socket

    @property
    def socket_lock(self):
        """
        Returns the threading lock object.

        :return: A threading lock object.
        """
        return self._socket_lock

    @property
    def is_debug(self):
        """
        Returns whether debugging is on or off.

        :return: True if debugging is on, False otherwise.
        """
        return self._debug

    @property
    def user_id(self):
        """
        Returns the user ID.

        :return: An integer representing the user ID.
        """
        return self._user_id

    @property
    def application_version(self):
        """
        Returns the Aqueduct Application version that the instance is connected to.

        :return: A str.
        """
        return self._application_version

    def is_local(self) -> bool:
        """
        Check if the IP address is a local address.

        :param address: (str) The IP address to check.
        :return: True if the IP address is local, False otherwise.
        """
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            return local_ip == self._address or self._address in [
                "127.0.0.1",
                "localhost",
                "::1",
            ]
        except Exception:  # pylint: disable=broad-except
            return False

    def is_lab_mode(self) -> bool:
        """
        Returns whether the application is running in Lab or Sim mode.

        :return: boolean.
        """
        return self.user_id == "L"

    @property
    def serial_number(self) -> typing.Union[int, None]:
        """
        Returns the user ID.

        :return: An integer representing the user ID.
        """
        return self._serial_number

    def send_and_wait_for_rx(
        self,
        message: str,
        response: str,
        attempts: int = SOCKET_TX_ATTEMPTS,
        timeout: int = 5,
        size: int = 1024 * 8,
        delay_s: typing.Union[None, float] = None,
    ):
        """
        Sends a message and waits for a response on the socket.

        Args:
            message (str): The message to send on the socket.
            response (str): The expected response from the socket.
            attempts (int): The number of attempts to send the message before giving up.
                Defaults to `SOCKET_TX_ATTEMPTS`.
            timeout (int): The maximum amount of time to wait for a response, in seconds.
                Defaults to 5 seconds.
            size (int): The size of the buffer to use when reading from the socket.
                Defaults to 8192 bytes.
            delay_s (float): The delay, in seconds, to wait between attempts to send the message.
                Defaults to None.

        Returns:
            The response from the socket, if it matches the expected response. None otherwise.
        """
        return send_and_wait_for_rx(
            message=message,
            sock=self.socket,
            lock=self.socket_lock,
            response=response,
            attempts=attempts,
            timeout=timeout,
            size=size,
            delay_s=delay_s,
        )

    def initialize(self, pause: typing.Union[bool, None] = None):
        """
        Initializes the Aqueduct instance.

        Args:
            pause (bool): Whether to pause the process after initialization. If None,
                it defaults to the value set during Aqueduct initialization.

        Note:
            If the Aqueduct instance is not running locally, a subprocess will be created to run the AqManager code.

        """
        self.register_process()

        time.sleep(0.005)

        self.get_setup(True)

        if self._register_process is False:
            return

        self._helper_t = threading.Thread(target=self._helper.run, daemon=True)
        self._helper_t.start()

        if not self.is_local():
            exe = sys.executable
            subprocess.Popen(
                [
                    exe,
                    "-c",
                    AqManager.code(),
                    f"-u {self._user_id}",
                    f"-a {self._address}",
                    f"-p {self._port}",
                    f"-i {self._pid}",
                    f"-d {int(self._debug)}",
                ],
            )

        if pause is None:
            pause = self._pause_on_queue

        if pause:
            self.update_process_status("queued")
            process = psutil.Process(os.getpid())
            process.suspend()
        else:
            self.update_process_status("running")

    def register_process(self):
        """
        Register a process with the Aqueduct server.

        :return: None
        """
        message = json.dumps(
            [SocketCommands.RegisterUser.value, self._user_id]
        ).encode()

        _loaded, payload = self.send_and_wait_for_rx(
            message, Events.REGISTERED_USER.value, SOCKET_TX_ATTEMPTS
        )

        try:
            payload = json.loads(payload)
            self._application_version = payload.get("application_version")
        except TypeError:
            warnings.warn("Application version not found in response.")

        if self._register_process is False:
            return

        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.REGISTER_PROCESS.value,
                    {"user_id": self._user_id, "pid": os.getpid()},
                ],
            ]
        ).encode()

        self.send_and_wait_for_rx(
            message,
            Events.REGISTER_PROCESS.value,
            SOCKET_TX_ATTEMPTS,
        )

    def set_command_delay(self, delay_s: float):
        """Sets the command delay for all devices.

        Args:
            delay_s (float): The delay in seconds to set.
        """
        for (_name, device) in self.devices.items():
            if isinstance(device, Device):
                device.command_delay = delay_s

    def pause_recipe(self):
        """Pauses the recipe associated with the current user ID."""
        if not self.is_local():
            message = json.dumps(
                [
                    SocketCommands.SocketMessage.value,
                    [Events.PAUSE_RECIPE.value, {"user_id": self._user_id}],
                ]
            ).encode()

            self.send_and_wait_for_rx(
                message,
                Events.PAUSE_RECIPE.value,
                SOCKET_TX_ATTEMPTS,
            )

        process = psutil.Process(self._pid)
        process.suspend()

    def update_process_status(self, status):
        """
        Sends a message to the Aqueduct server to update the status of the current process.

        :param status: The new status of the process.
        :type status: str
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.UPDATE_PROCESS.value,
                    {"user_id": self._user_id, "status": status},
                ],
            ]
        ).encode()

        self.send_and_wait_for_rx(
            message,
            Events.UPDATE_PROCESS.value,
            SOCKET_TX_ATTEMPTS,
        )

    def get_setup(self, update: bool = True):
        """
        Sends a message to the Aqueduct server to get the current setup information.

        :param update: Whether or not to update the current `devices` dictionary with any newly added devices.
        :type update: bool, defaults to True
        :return: The current setup information.
        :rtype: dict
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.GET_SETUP.value, {"user_id": self._user_id}],
            ]
        ).encode()

        _loaded, payload = self.send_and_wait_for_rx(
            message,
            Events.GET_SETUP.value,
            SOCKET_TX_ATTEMPTS,
            size=1024 * 64,
        )

        payload = json.loads(payload)

        if payload:
            if update:
                devices = payload.get("devices")
                for _k, v in devices.items():
                    dev_obj = v.get("device")
                    device = create_device(
                        dev_obj.get("base").get("type"),
                        self._socket,
                        self._socket_lock,
                        **dev_obj,
                    )
                    self.devices.update({dev_obj.get("base").get("name"): device})
            return payload
        return None

    def clear_setup(self):
        """
        Sends a message to the Aqueduct server to clear the current setup information.
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.CLEAR_SETUP.value, dict(user_id=self._user_id)],
            ]
        ).encode()

        self.send_and_wait_for_rx(message, Events.CLEAR_SETUP.value, SOCKET_TX_ATTEMPTS)

    def add_device(
        self,
        kind: DeviceTypes,
        name: typing.Optional[str] = None,
        size: typing.Optional[int] = None,
    ):
        """
        Add a device to the setup.

        :param kind: Type of the device to add.
        :type kind: str
        :param name: Name of the device, defaults to None
        :type name: str, optional
        :param size: Number of `nodes` to create, defaults to None
        :type size: int, optional
        """
        if size is None:
            size = 1

        payload = dict(
            device_type=kind.value,
            name=name,
            size=size,
            interface=0,  # sim
            kind=0,  # sim
        )

        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.ADD_DEVICE.value,
                    payload,
                ],
            ]
        ).encode()

        self.send_and_wait_for_rx(message, Events.ADD_DEVICE.value, SOCKET_TX_ATTEMPTS)

    def set_log_file_name(self, log_file_name: str):
        """Set the log file name."""
        self._logger.set_log_file_name(log_file_name)

    def log(self, message):
        """
        Logs a message with severity 'DEBUG'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.log(message)

    def debug(self, message):
        """
        Logs a message with severity 'DEBUG'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.debug(message)

    def info(self, message):
        """
        Logs a message with severity 'INFO'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.info(message)

    def warning(self, message):
        """
        Logs a message with severity 'WARNING'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.warning(message)

    def error(self, message):
        """
        Logs a message with severity 'ERROR'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.error(message)

    def critical(self, message):
        """
        Logs a message with severity 'CRITICAL'.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        self._logger.critical(message)

    def prompt(
        self,
        message: str = None,
        timeout_s: typing.Union[int, float] = None,
        pause_recipe: bool = True,
    ) -> Prompt:
        """
        Creates a new Prompt object.

        :param message: Prompt message to display, defaults to None
        :type message: str, optional
        :param timeout_s: Timeout duration for the prompt in seconds, defaults to None
        :type timeout_s: typing.Union[int, float], optional
        :param pause_recipe: If True, pauses the recipe upon calling the prompt, defaults to True
        :type pause_recipe: bool, optional
        :return: A new Prompt object
        :rtype: aqueduct.core.prompt.Prompt
        """
        p = Prompt(message, timeout_s, pause_recipe)
        p.assign(self)
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.SET_RECIPE_PROMPT.value,
                    dict(prompt={**dict(user_id=self._user_id), **p.serialize()}),
                ],
            ]
        ).encode()

        self.send_and_wait_for_rx(
            message,
            Events.SET_RECIPE_PROMPT.value,
            SOCKET_TX_ATTEMPTS,
        )

        if pause_recipe:
            self.pause_recipe()

        return p

    def input(
        self,
        message: str = None,
        timeout_s: typing.Union[int, float] = None,
        pause_recipe: bool = True,
        input_type: str = UserInputTypes.TEXT_INPUT.value,
        options: list = None,
        rows: list = None,
        dtype: str = None,
    ) -> Input:
        """
        Creates a new Input object.

        :param message: Input message to display, defaults to None
        :type message: str, optional
        :param timeout_s: Timeout duration for the input in seconds, defaults to None
        :type timeout_s: typing.Union[int, float], optional
        :param pause_recipe: If True, pauses the recipe upon calling the input, defaults to True
        :type pause_recipe: bool, optional
        :param input_type: The type of input widget to display, defaults to UserInputTypes.TEXT_INPUT.value
        :type input_type: str, optional
        :param options: A list of options to display if input_type is UserInputTypes.DROPDOWN.value or UserInputTypes.BUTTONS.value, defaults to None
        :type options: list, optional
        :param rows: A list of rows to display if input_type is UserInputTypes.TABLE.value or UserInputTypes.CSV_UPLOAD.value, defaults to None
        :type rows: list, optional
        :param dtype: The data type of the input value, defaults to None
        :type dtype: str, optional
        :return: A new Input object
        :rtype: aqueduct.core.input.Input
        """
        ipt = Input(
            message=message,
            timeout_s=timeout_s,
            pause_recipe=pause_recipe,
            input_type=input_type,
            options=options,
            rows=rows,
            dtype=dtype,
        )

        ipt.assign(self)

        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.SET_RECIPE_INPUT.value,
                    dict(input={**dict(user_id=self._user_id), **ipt.serialize()}),
                ],
            ]
        ).encode()

        self._socket.settimeout(1)

        self.send_and_wait_for_rx(
            message,
            Events.SET_RECIPE_INPUT.value,
            SOCKET_TX_ATTEMPTS,
        )

        if pause_recipe:
            self.pause_recipe()

        return ipt

    def register_input(self, ipt: Input):
        """
        Register an Input object.

        :param ipt: The Input object to register
        :type ipt: aqueduct.core.input.Input
        """
        ipt.assign(self)

    def setpoint(
        self,
        name: str,
        value: typing.Union[float, int, bool, str, datetime.datetime, list],
        dtype: str = None,
    ) -> Setpoint:
        """
        Creates a new Setpoint object.

        :param name: The name of the setpoint
        :type name: str
        :param value: The initial value of the setpoint
        :type value: typing.Union[float, int, bool, str, datetime.datetime, list]
        :param dtype: The data type of the setpoint value, defaults to None
        :type dtype: str, optional
        :return: A new Setpoint object
        :rtype: aqueduct.core.setpoint.Setpoint
        """
        s = Setpoint(name, value, dtype)
        self.register_setpoint(s)
        self.update_setpoint(s)
        return s

    def recordable(
        self,
        name: str,
        value: typing.Union[float, int, bool, str, datetime.datetime, list],
        dtype: str = None,
    ) -> Recordable:
        """
        Creates a new Recordable object and registers it with Aqueduct.

        :param name: The name of the Recordable.
        :type name: str
        :param value: The initial value of the Recordable.
        :type value: Union[float, int, bool, str, datetime.datetime, list]
        :param dtype: The data type of the Recordable value, defaults to None.
        :type dtype: str, optional
        :return: The newly created Recordable object.
        :rtype: Recordable
        """
        recordable = Recordable(name, value, dtype)
        self.register_recordable(recordable)
        self.update_recordable(recordable)
        return recordable

    def register_setpoint(self, setpoint: Setpoint):
        """
        Registers a Setpoint object with Aqueduct.

        :param setpoint: The Setpoint object to register.
        :type setpoint: Setpoint
        """
        setpoint.assign(self)
        self._setpoints.update({setpoint.name: setpoint})

    def register_recordable(self, recordable: Recordable):
        """
        Registers a Recordable object with Aqueduct.

        :param recordable: The Recordable object to register.
        :type recordable: Recordable
        """
        recordable.assign(self)
        self._recordables.update({recordable.name: recordable})

    def update_setpoint(self, setpoint: Setpoint):
        """
        Updates a Recordable object's value on the Aqueduct server.

        :param recordable: The Recordable object to update.
        :type recordable: Recordable
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.UPDATE_USER_PARAMS.value, dict(params=[setpoint.serialize()])],
            ]
        ).encode()

        i = 0
        while i < SOCKET_TX_ATTEMPTS:
            try:
                with self._socket_lock:
                    self._socket.settimeout(1)
                    self._socket.send(message)
                    time.sleep(SOCKET_DELAY_S)
                    data = self._socket.recv(1024 * 8)
                packets = split_packets(data)
                for packet in packets:
                    command = json.loads(packet)
                    if command[0] == Events.UPDATED_USER_PARAMS.value:
                        return
            except (json.decoder.JSONDecodeError, socket.timeout) as err:
                if self.is_debug:
                    print(f"update_setpoint error: {err}")
                continue
            i += 1

    def update_recordable(self, recordable: Recordable):
        """
        Update the value of a recordable.

        Args:
            recordable (Recordable): the recordable object to update.

        Raises:
            ValueError: if the recordable is not found.
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.UPDATE_USER_RECORDABLES.value,
                    dict(params=[recordable.serialize()]),
                ],
            ]
        ).encode()

        self.send_and_wait_for_rx(
            message,
            Events.UPDATE_USER_RECORDABLES.value,
            SOCKET_TX_ATTEMPTS,
        )

    def clear_recordable(self, recordable: Recordable):
        """
        Remove a recordable from the user's recordables.

        Args:
            recordable (Recordable): the recordable object to remove.

        Raises:
            ValueError: if the recordable is not found.
        """
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [Events.CLEAR_USER_RECORDABLES.value, dict(params=[recordable.name])],
            ]
        ).encode()

        self.send_and_wait_for_rx(
            message,
            Events.CLEAR_USER_RECORDABLES.value,
            SOCKET_TX_ATTEMPTS,
        )

    def handle_updated_setpoint(self, setpoint: dict):
        """
        Handle a new value for a setpoint received from the server.

        Args:
            setpoint (dict): a dictionary containing the updated setpoint.

        Raises:
            ValueError: if the setpoint is not found.
        """
        dtype = setpoint.get("d")
        value = setpoint.get("v")
        setpoint: Setpoint = self._setpoints.get(setpoint.get("n"))

        if dtype == int.__name__:
            value = int(value)
        elif dtype == float.__name__:
            value = float(value)
        elif dtype == str.__name__:
            value = str(value)
        elif dtype == bool.__name__:
            value = string_to_bool(value)
        elif dtype == datetime.datetime.__name__:
            value = str(value)

        setpoint.value = value

        if callable(setpoint.on_change):
            setpoint.on_change(*setpoint.args, **setpoint.kwargs)

    def remove_setpoint(self, setpoint: Setpoint):
        """
        Remove a setpoint from the user's setpoints.

        Args:
            setpoint (Setpoint): the setpoint object to remove.

        Raises:
            ValueError: if the setpoint is not found.
        """
        self._setpoints.pop(setpoint.name)

    def remove_recordable(self, recordable: Recordable):
        """
        Remove a recordable from the user's recordables.

        Args:
            recordable (Recordable): the recordable object to remove.

        Raises:
            ValueError: if the recordable is not found.
        """
        self._setpoints.pop(recordable.name)

    def pid_controller(
        self,
        name: typing.Optional[str],
        input_data: AccessorData,
        output_data: AccessorData,
        pid_params: Pid,
    ) -> PidController:
        """
        Create and register a new PidController instance.

        :param name: Optional name of the PID controller.
        :type name: Optional[str]
        :param input_data: Data for the input accessor.
        :type input_data: AccessorData
        :param output_data: Data for the output accessor.
        :type output_data: AccessorData
        :param pid_params: The PID control parameters.
        :type pid_params: Pid

        :return: The created PidController instance.
        :rtype: PidController
        """
        controller = PidController(name, input_data, output_data, pid_params)
        self.register_pid_controller(controller)
        self.create_pid_controller(controller)
        return controller

    def register_pid_controller(self, controller: PidController):
        """
        Register a PidController instance.

        :param controller: The PidController instance to register.
        :type controller: PidController
        """
        # pylint: disable=protected-access
        controller._assign(self)

    def create_pid_controller(self, controller: PidController):
        """
        Create a PidController.

        Args:
            controller (PidController): the PidController object to create.

        Raises:
            ValueError: if the PidController is not found.
        """
        # pylint: disable=protected-access
        if not isinstance(controller._aq, Aqueduct):
            # pylint: disable=protected-access
            controller._assign(self)

        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    # pylint: disable=protected-access
                    Events.CREATE_PID_CONTROLLERS.value,
                    dict(controllers=[controller._serialize()]),
                ],
            ]
        ).encode()

        _ok, response = self.send_and_wait_for_rx(
            message,
            Events.CREATED_PID_CONTROLLERS.value,
            SOCKET_TX_ATTEMPTS,
            delay_s=0.05,
        )

        try:
            while isinstance(response, str):
                response = json.loads(response)
            controller_id = int(list(response.get("controllers").keys())[0])
            controller._set_id(controller_id)
        except json.decoder.JSONDecodeError as error:
            warnings.warn(f"Failed to create PID controller: {error}")


class AqHelper:
    """
    The `AqHelper` class is responsible for handling user parameter updates and other events
    sent by the Aqueduct server.

    Attributes:
        _aq (Aqueduct): The `Aqueduct` instance associated with this helper.
        _run (bool): A flag indicating whether the helper should continue running.
        _socket (socket.socket): The socket used to communicate with the Aqueduct server.
        _update_frequency_s (float): The frequency at which to check for updated user parameters.

    Methods:
        __init__(aq: Aqueduct, address: str = "127.0.0.1", port: int = 59000):
            Creates a new `AqHelper` instance and establishes a socket connection with the
            Aqueduct server.
        shutdown():
            Stops the helper from running.
        run():
            Begins processing events sent by the Aqueduct server.
        handle_updated_user_params(message: str):
            Updates the setpoint values in the associated `Aqueduct` instance with the values
            provided in the message.

    """

    _aq: Aqueduct
    _run: bool = True
    _socket: socket.socket

    _update_frequency_s: float = 0.001

    def __init__(self, aq: Aqueduct, address: str = "127.0.0.1", port: int = 59000):
        """Initialize the `AqHelper` object.

        :param aq: (Aqueduct) The `Aqueduct` instance to which this `AqHelper` belongs.
        :param address: (str) The IP address of the Aqueduct server.
        :param port: (int) The port on which to connect to the Aqueduct server.
        """
        self._aq = aq
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((address, port))

        message = json.dumps(
            [SocketCommands.RegisterUser.value, self._aq.user_id]
        ).encode()

        send_and_wait_for_rx(message, self._socket, None, OK, SOCKET_TX_ATTEMPTS)

        message = json.dumps(
            [
                SocketCommands.RegisterEvents.value,
                [
                    Events.UPDATED_USER_PARAMS.value,
                ],
            ]
        ).encode()

        send_and_wait_for_rx(message, self._socket, None, OK, SOCKET_TX_ATTEMPTS)

    def shutdown(self):
        """Shut down the `AqHelper` object."""
        self._run = False

    def run(self):
        """Continuously receives data from the socket connection and processes it.

        If the received data contains updated user parameters, calls the
        `handle_updated_user_params` method with the updated parameters.
        If an exception is raised while processing the data, the exception is printed
        if debug mode is enabled. The method runs until `_run` is set to False.
        """
        while self._run:
            try:
                while True:
                    data = self._socket.recv(1024 * 16)
                    packets = split_packets(data)
                    for packet in packets:
                        command = json.loads(packet)
                        if command[0] == Events.UPDATED_USER_PARAMS.value:
                            self.handle_updated_user_params(json.loads(command[1]))
                    time.sleep(self._update_frequency_s)
            except BaseException as err:  # pylint: disable=broad-except
                if self._aq.is_debug:
                    print(f"AqHelper error: {err}")

    def handle_updated_user_params(self, message):
        """Processes updated user parameters and calls `handle_updated_setpoint` with each updated parameter.

        :param message: A list of dictionaries representing the updated parameters.
        """
        for p in message:
            self._aq.handle_updated_setpoint(p)


class AqManager:
    """
    A class for managing the connection and communication with the Aqueduct application server.

    Args:
        main_pid (int): The process ID of the main process.
        user_id (Union[int, str]): The ID of the user to register with the application server.
        address (str): The IP address of the application server.
        port (int): The port number of the application server.
        debug (bool): Whether to enable debug mode.

    Attributes:
        _pid (int): The process ID of the main process.
        _user_id (Union[int, str]): The ID of the user registered with the application server.
        _run (bool): Whether the manager should continue to run.
        _socket (socket.socket): The socket used to communicate with the application server.
        _debug (bool): Whether debug mode is enabled.
        _update_frequency_s (float): The frequency at which the manager checks for updates from the application server.

    """

    _pid: int
    _user_id: typing.Union[int, str]
    _run: bool = True
    _socket: socket.socket
    _debug: bool = False

    _update_frequency_s: float = 0.001

    def __init__(
        self,
        main_pid: int,
        user_id: typing.Union[int, str],
        address: str = "127.0.0.1",
        port: int = 59000,
        debug: bool = False,
    ):
        """
        Initializes an `AqManager` instance.

        Args:
            main_pid (int): The process ID of the main process.
            user_id (Union[int, str]): The ID of the user to register with the application server.
            address (str): The IP address of the application server.
            port (int): The port number of the application server.
            debug (bool): Whether to enable debug mode.
        """
        self._pid = main_pid
        self._user_id = user_id
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._debug = debug

        self._socket.connect((address, port))

        message = json.dumps([SocketCommands.RegisterUser.value, user_id]).encode()

        _response = send_and_wait_for_rx(
            message, self._socket, None, OK, SOCKET_TX_ATTEMPTS
        )

        message = json.dumps(
            [
                SocketCommands.RegisterEvents.value,
                [
                    "recipe_status",
                ],
            ]
        ).encode()

        send_and_wait_for_rx(message, self._socket, None, OK, SOCKET_TX_ATTEMPTS)

    @classmethod
    def code(cls) -> str:
        """
        Returns a string of code that can be used to create and run an instance of `AqManager`.

        Returns:
            str: A string of code that can be used to create and run an instance of `AqManager`.
        """
        return """
from aqueduct.core.aq import AqManager

manager = AqManager.parse()
manager.run()
"""

    def shutdown(self):
        """
        Stops the manager from running.
        """
        self._run = False

    @classmethod
    def parse(cls):
        """
        Parses command line arguments to create an `AqManager` instance.

        Returns:
            A new `AqManager` instance with parsed command line arguments.
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-u", "--user_id", type=str, help="user_id (either int or 'L')", default="1"
        )

        parser.add_argument(
            "-a",
            "--addr",
            type=str,
            help="IP address (no port, like 127.0.0.1)",
            default="127.0.0.1",
        )

        parser.add_argument(
            "-p", "--port", type=int, help="port (like 59000)", default=59000
        )

        parser.add_argument(
            "-i",
            "--pid",
            type=int,
            help="Process ID (pid)",
            default=0,
        )

        parser.add_argument(
            "-d",
            "--debug",
            type=int,
            help="Debug",
            default=0,
        )

        args = parser.parse_args()

        user_id = args.user_id.strip()
        ip_address = args.addr.strip()
        port = int(args.port)
        pid = int(args.pid)
        debug = int(args.debug)

        return cls(pid, user_id, ip_address, port, debug)

    def run(self):
        """Starts the Aqueduct manager.

        This method runs indefinitely, continuously listening for incoming messages from the Aqueduct application server and
        handling them appropriately. If the process ID specified during initialization cannot be found, the method will
        terminate.

        Returns:
            None
        """
        while self._run:
            try:
                while True:
                    data = self._socket.recv(1024 * 16)
                    packets = split_packets(data)
                    for packet in packets:
                        command = json.loads(packet)
                        if command[0] == Events.RECIPE_STATUS.value:
                            self.handle_recipe_status(json.loads(command[1]))
                    time.sleep(self._update_frequency_s)

            except json.JSONDecodeError as err:
                if self._debug:
                    print(f"AqManager JSON decode error: {err}")
            except ConnectionResetError as err:
                if self._debug:
                    print(f"AqManager connection reset error: {err}")
            except Exception as err:  # pylint: disable=broad-except
                if self._debug:
                    print(f"AqManager error: {err}")

            try:
                psutil.Process(self._pid)
            except psutil.NoSuchProcess:
                self._run = False
                break

        if self._debug:
            print("AqManager shutting down...")

    def handle_recipe_status(self, payload):
        """Handles recipe status messages.

        This method is called by `run()` whenever a new recipe status message is received from the Aqueduct application
        server. If the status indicates that the recipe should be paused or stopped, the process specified during
        initialization will be suspended. If the status indicates that the recipe should continue running, the process will
        be resumed.

        Args:
            payload (str): The recipe status message received from the Aqueduct application server.

        Returns:
            None
        """
        if payload == "pause_recipe" or payload == "estop_recipe":
            process = psutil.Process(self._pid)
            process.suspend()
        elif payload == "run_recipe":
            process = psutil.Process(self._pid)
            process.resume()
