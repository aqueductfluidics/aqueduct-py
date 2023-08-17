from typing import Optional, Tuple
import json
from enum import Enum

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
        delta_output_limit (Optional[float]): Maximum allowable change in output.
        control_bounds (Tuple[Optional[float], Optional[float]]): Bounds for integral accumulation.
        output_limits (Tuple[Optional[float], Optional[float]]): Overall output filter limits.
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
    delta_output_limit: Optional[float]
    control_bounds: Tuple[Optional[float], Optional[float]]
    output_limits: Tuple[Optional[float], Optional[float]]

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
        self.delta_output_limit = None
        self.control_bounds = control_bounds
        self.output_limits = output_limits

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
        self._aq = None

    def assign(self, aqueduct: "Aqueduct"):
        """
        Set an Aqueduct instance for this PID controller.

        Args:
            aqueduct (Aqueduct): An instance of Aqueduct.
        """
        self._aq = aqueduct

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

    def to_json(self):
        """
        Convert this Setpoint object to a JSON string representation.

        :return: A JSON string representing the PID controller object.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.serialize())

    def initialize(self):
        """
        Initialize the PID controller.
        """
        pass

    def update(self):
        """
        Update the PID controller.
        """
        pass

    def control(self, setpoint: float):
        """
        Control the process using the PID controller.

        Args:
            setpoint (float): The desired setpoint value.
        """
        pass
