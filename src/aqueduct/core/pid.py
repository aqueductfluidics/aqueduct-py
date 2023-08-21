from typing import Optional, Tuple, List
import json
from enum import Enum
import warnings

from aqueduct.core.socket_constants import Events
from aqueduct.core.socket_constants import SOCKET_TX_ATTEMPTS
from aqueduct.core.socket_constants import SocketCommands

# pylint: disable=invalid-name


class AccessorKind(Enum):
    """
    Enumeration of AccessorKind units.
    """
    MassFlow = 0
    Ph = 1
    Pressure = 2
    Temperature = 3
    Weight = 4
    PeristalicticRate = 5
    SyringeRate = 6
    PeristalticStatus = 7
    SyringeStatus = 8
    Position = 9


class AccessorData:
    """
    Class representing accessor data.

    Attributes:
        kind (int): Kind of accessor.
        units (int): Units of the accessor.
        device_size (int): Size of the device.
        index (int): Index of the accessor.
    """

    def __init__(
        self,
        kind: int,
        units: int,
        device_id: int,
        index: int
    ):
        self.kind = kind
        self.units = units
        self.device_id = device_id
        self.index = index

    def serialize(self):
        """
        Serialize the PID object.

        Returns:
            dict: a dictionary representation of the PID object
        """
        serialized = self.__dict__.copy()

        for key, value in serialized.items():
            if isinstance(value, tuple):
                serialized[key] = list(value)

        return serialized


class Controller:
    """
    Class representing the parameterized PID controller.


    """
    bias: float
    kp: float
    ki: float
    kd: float
    linearity: float
    beta: float
    setpoint_range: float
    p_limit: Optional[float]
    i_limit: Optional[float]
    d_limit: Optional[float]
    delta_limit: Optional[float]
    integral_valid: Optional[float]
    dead_zone: Optional[float]

    def __init__(
        self,
        **kwargs,
    ):
        self._init_defaults()
        valid_attributes = {
            "bias": float,
            "kp": float,
            "ki": float,
            "kd": float,
            "linearity": float,
            "beta": float,
            "setpoint_range": float,
            "p_limit": (float, type(None)),
            "i_limit": (float, type(None)),
            "d_limit": (float, type(None)),
            "delta_limit": (float, type(None)),
            "integral_valid": (float, type(None)),
            "dead_zone": (float, type(None))
        }

        for key, value in kwargs.items():
            if key in valid_attributes and isinstance(value, valid_attributes[key]):
                setattr(self, key, value)

    def _init_defaults(self):
        """Default initializer."""
        self.bias = 0.0
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0
        self.linearity = 1.0
        self.beta = 1.0
        self.setpoint_range = 1.0
        self.p_limit = None
        self.i_limit = None
        self.d_limit = None
        self.delta_limit = None
        self.integral_valid = None
        self.dead_zone = None

    def serialize(self):
        return {
            "bias": self.bias,
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "linearity": self.linearity,
            "beta": self.beta,
            "setpoint_range": self.setpoint_range,
            "p_limit": [self.p_limit, None] if self.p_limit else [None, True],
            "i_limit": [self.i_limit, None] if self.i_limit else [None, True],
            "d_limit": [self.d_limit, None] if self.d_limit else [None, True],
            "delta_limit": [self.delta_limit, None] if self.delta_limit else [None, True],
            "integral_valid": [self.integral_valid, None] if self.integral_valid else [None, True],
            "dead_zone": [self.dead_zone, None] if self.dead_zone else [None, True],
        }

class ControllerSchedule:
    process: Optional[Tuple[float, float]]
    error: Optional[Tuple[float, float]]
    control: Optional[Tuple[float, float]]

    def __init__(
        self,
        **kwargs,
    ):
        self._init_defaults()
        valid_attributes = {
            "process": (tuple, type(None)),
            "error": (tuple, type(None)),
            "control": (tuple, type(None)),
        }

        for key, value in kwargs.items():
            if key in valid_attributes and isinstance(value, valid_attributes[key]):
                setattr(self, key, value)

    def _init_defaults(self):
        """Default initializer."""
        self.process = None
        self.error = None
        self.control = None

    def serialize(self) -> dict:
        """
        Serialize the PID object.

        Returns:
            dict: a dictionary representation of the PID object
        """
        return self.__dict__


class Schedule:
    controller: Controller
    schedule: ControllerSchedule

    def __init__(
        self,
        controller: Controller,
        schedule: Optional[ControllerSchedule] = None
    ):
        self.controller = controller
        if schedule is None:
            schedule = ControllerSchedule()
        self.schedule = schedule

    def serialize(self) -> dict:
        """
        Serialize the PID object.

        Returns:
            dict: a dictionary representation of the PID object
        """
        return {
            **self.schedule.serialize(),
            **self.controller.serialize(),
        }


class Pid:
    """
    Class representing a PID controller.

    Attributes:
        enabled (bool): Enable / Disable the PID controller. Will output None when disabled.
        update_interval (timedelta): Time interval between updates.
        setpoint (float): Ideal setpoint to strive for.
        output_limits (Tuple[Optional[float], Optional[float]]): Overall output filter limits.
    """

    enabled: bool
    update_interval_ms: int
    setpoint: float
    schedule: List[Schedule]
    integral_term: float
    output_limits: Tuple[Optional[float], Optional[float]]

    def __init__(
        self,
        setpoint: float,
        update_interval_ms: int = 1000,
        **kwargs,
    ):
        self._init_defaults()
        valid_attributes = {
            "enabled": bool,
            "update_interval_ms": int,
            "setpoint": float,
            "integral_term": float,
            "output_limits": (tuple,),
        }

        self.setpoint = setpoint
        self.update_interval_ms = update_interval_ms

        for key, value in kwargs.items():
            if key in valid_attributes and isinstance(value, valid_attributes[key]):
                setattr(self, key, value)
            else:
                pass

    def _init_defaults(self):
        """Default initiailzer."""
        self.enabled = False
        self.update_interval_ms = 1000
        self.setpoint = 0.0
        self.integral_term = 0.0
        self.schedule = []
        self.output_limits = (None, None)

    def add_schedule(self, schedule: Schedule):
        self.schedule.append(schedule)

    def serialize(self) -> dict:
        """
        Serialize the PID object.

        Returns:
            dict: a dictionary representation of the PID object
        """
        return {
            "enabled": self.enabled,
            "update_interval_ms": self.update_interval_ms,
            "setpoint": self.setpoint,
            "integral_term": self.integral_term,
            "schedule": [s.serialize() for s in self.schedule],
            "output_limits": list(self.output_limits),
        }

class PidController:

    """
    Class representing a PID controller.

    Attributes:
        name (Optional[str]): Optional name of the PID controller.
        input (AccessorData): Data for the input accessor.
        output (AccessorData): Data for the output accessor.
        pid (Pid): The PID control parameters.
        _aq ("Aqueduct"): Internal reference to an Aqueduct instance.
    """

    def __init__(
        self,
        name: Optional[str],
        input_data: AccessorData,
        output_data: AccessorData,
        pid_params: Pid,
    ):
        self.name = name
        self.input = input_data
        self.output = output_data
        self.pid = pid_params
        self._id = None
        self._aq = None

    def assign(self, aqueduct: "Aqueduct"):
        """
        Set an Aqueduct instance for this PID controller.

        Args:
            aqueduct (Aqueduct): An instance of Aqueduct.
        """
        self._aq = aqueduct

    def set_id(self, controller_id: int):
        """
        Set an Aqueduct instance for this PID controller.

        Args:
            aqueduct (Aqueduct): An instance of Aqueduct.
        """
        self._id = controller_id

    def serialize(self) -> dict:
        """
        Serialize the PID controller object.

        Returns:
            dict: a dictionary representation of the PID controller object
        """
        return {
            "name": self.name,
            "input": self.input.serialize(),
            "output": self.output.serialize(),
            "pid": self.pid.serialize(),
        }

    def serialize_update(self) -> dict:
        """
        Serialize the PID controller object.

        Returns:
            dict: a dictionary representation of the PID controller object
        """
        return {
            "id": self._id,
            "pid": self.pid.serialize(),
        }

    def to_json(self):
        """
        Convert this Setpoint object to a JSON string representation.

        :return: A JSON string representing the PID controller object.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.serialize())

    def change_setpoint(self, setpoint: float, clear_integral: bool = False):
        """
        Change the setpoint of the PID controller.
        """
        self.pid.setpoint = setpoint
        if clear_integral:
            self.pid.integral_term = 0.0
        self._update()

    def enable(self):
        """
        Enable the PID controller.
        """
        self.pid.enabled = True
        self._update()

    def disable(self):
        """
        Disable the PID controller.
        """
        self.pid.enabled = False
        self._update()

    def change_parameters(self, kp=None, ki=None, kd=None, bias=None):
        """
        Change the PID parameters.

        Args:
            kp (float): New proportional gain.
            ki (float): New integral gain.
            kd (float): New derivative gain.
        """
        if kp is not None:
            self.pid.kp = kp
        if ki is not None:
            self.pid.ki = ki
        if kd is not None:
            self.pid.kd = kd
        if bias is not None:
            self.pid.bias = bias
        self._update()

    def clear_integral(self):
        """
        Clear the integral term of the PID controller.
        """
        self.pid.integral_term = 0.0
        self._update()

    def _update(self):
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.UPDATE_PID_CONTROLLERS.value,
                    dict(controllers=[self.serialize_update()]),
                ],
            ]
        ).encode()

        _ok, response = self._aq.send_and_wait_for_rx(
            message,
            Events.UPDATED_PID_CONTROLLERS.value,
            SOCKET_TX_ATTEMPTS,
        )

        try:
            while isinstance(response, str):
                response = json.loads(response)

            controllers = response.get("controllers", {})
            updated_controller = controllers.get(str(self._id))

            if updated_controller:
                updated_pid = updated_controller.get("pid")
                if updated_pid:
                    self.pid = Pid(**updated_pid)

        except json.decoder.JSONDecodeError as error:
            warnings.warn(f"Failed to update PID controller: {error}")
