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
        return self.__dict__


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
    kp: float
    ki: float
    kd: float
    p_limit: Optional[float]
    i_limit: Optional[float]
    d_limit: Optional[float]
    delta_limits: Optional[Tuple[float, float]]
    control_bounds: Tuple[Optional[float], Optional[float]]
    output_limits: Tuple[Optional[float], Optional[float]]
    dead_zone: Optional[Tuple[float, float]]

    def __init__(
        self,
        setpoint: float,
        update_interval_ms: int,
        control_bounds: Tuple[Optional[float], Optional[float]],
        output_limits: Tuple[Optional[float], Optional[float]]
    ):
        self.enabled = False
        self.update_interval_ms = update_interval_ms
        self.setpoint = setpoint
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0
        self.p_limit = None
        self.i_limit = None
        self.d_limit = None
        self.delta_limits = None
        self.control_bounds = control_bounds
        self.output_limits = output_limits
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
            print(response)
        except json.decoder.JSONDecodeError as error:
            warnings.warn(f"Failed to update PID controller: {error}")
