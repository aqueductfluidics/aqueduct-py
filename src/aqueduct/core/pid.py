from typing import Optional, Tuple
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


class Pid:
    """
    Class representing a PID controller.

    Attributes:
        enabled (bool): Enable / Disable the PID controller. Will output None when disabled.
        update_interval (timedelta): Time interval between updates.
        setpoint (float): Ideal setpoint to strive for.
        kp (float): Proportional gain.
        ki (float): Integral gain.
        kd (float): Derivative gain.
        p_limit (Optional[float]): Limiter for the proportional term.
        i_limit (Optional[float]): Limiter for the integral term.
        d_limit (Optional[float]): Limiter for the derivative term.
        delta_limits (Optional[float]): Maximum allowable change in output, (max_decrement, max_increment).
        control_bounds (Tuple[Optional[float], Optional[float]]): Bounds for integral accumulation.
        output_limits (Tuple[Optional[float], Optional[float]]): Overall output filter limits.
        dead_zone (Optional[float]): Defines the region around the setpoint 
          where the controller does not manipulate the output, (lower bound, upper bound).
    """

    enabled: bool
    update_interval_ms: int
    setpoint: float
    bias: float
    kp: float
    ki: float
    kd: float
    p_limit: Optional[float]
    i_limit: Optional[float]
    d_limit: Optional[float]
    integral_term: float
    delta_limits: Optional[Tuple[float, float]]
    control_bounds: Tuple[Optional[float], Optional[float]]
    output_limits: Tuple[Optional[float], Optional[float]]
    dead_zone: Optional[Tuple[float, float]]

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
            "bias": float,
            "kp": float,
            "ki": float,
            "kd": float,
            "p_limit": (float, type(None)),
            "i_limit": (float, type(None)),
            "d_limit": (float, type(None)),
            "integral_term": float,
            "delta_limits": (tuple, type(None)),
            "control_bounds": (tuple,),
            "output_limits": (tuple,),
            "dead_zone": (tuple, type(None))
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
        self.bias = 0.0
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0
        self.p_limit = None
        self.i_limit = None
        self.d_limit = None
        self.integral_term = 0.0
        self.delta_limits = None
        self.control_bounds = (None, None)
        self.output_limits = (None, None)
        self.dead_zone = None

    def serialize(self) -> dict:
        """
        Serialize the PID object.

        Returns:
            dict: a dictionary representation of the PID object
        """
        return self.__dict__


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
