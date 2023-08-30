import json
import warnings
from enum import Enum
from typing import List
from typing import Optional
from typing import Tuple

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
    OpticalDensity = 10


class AccessorData:
    """
    Class representing accessor data.

    Attributes:
        kind (int): Kind of accessor.
        units (int): Units of the accessor.
        device_size (int): Size of the device.
        index (int): Index of the accessor.
    """

    def __init__(self, kind: int, units: int, device_id: int, index: int):
        self.kind = kind
        self.units = units
        self.device_id = device_id
        self.index = index

    def _serialize(self):
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


class ScheduleParameters:
    """
    Class representing the parameters for a controller schedule.

    Attributes:
        bias (float): The bias value.
        kp (float): The proportional gain.
        ki (float): The integral gain.
        kd (float): The derivative gain.
        linearity (float): The linearity value.
        beta (float): The beta value.
        setpoint_range (float): The setpoint range value.
        p_limit (Optional[float]): The proportional limit value.
        i_limit (Optional[float]): The integral limit value.
        d_limit (Optional[float]): The derivative limit value.
        delta_limit (Optional[float]): The delta limit value.
        integral_valid (Optional[float]): The integral valid value.
        dead_zone (Optional[float]): The dead zone value.
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
        bias: Optional[float] = None,
        kp: Optional[float] = None,
        ki: Optional[float] = None,
        kd: Optional[float] = None,
        linearity: Optional[float] = None,
        beta: Optional[float] = None,
        setpoint_range: Optional[float] = None,
        p_limit: Optional[float] = None,
        i_limit: Optional[float] = None,
        d_limit: Optional[float] = None,
        delta_limit: Optional[float] = None,
        integral_valid: Optional[float] = None,
        dead_zone: Optional[float] = None,
    ):
        """
        Initialize a Controller object.

        Args:
            bias (Optional[float]): The bias value.
            kp (Optional[float]): The proportional gain.
            ki (Optional[float]): The integral gain.
            kd (Optional[float]): The derivative gain.
            linearity (Optional[float]): The linearity value.
            beta (Optional[float]): The beta value.
            setpoint_range (Optional[float]): The setpoint range value.
            p_limit (Optional[float]): The proportional limit value.
            i_limit (Optional[float]): The integral limit value.
            d_limit (Optional[float]): The derivative limit value.
            delta_limit (Optional[float]): The delta limit value.
            integral_valid (Optional[float]): The integral valid value.
            dead_zone (Optional[float]): The dead zone value.
        """
        self._init_defaults()

        if bias is not None:
            self.bias = bias
        if kp is not None:
            self.kp = kp
        if ki is not None:
            self.ki = ki
        if kd is not None:
            self.kd = kd
        if linearity is not None:
            self.linearity = linearity
        if beta is not None:
            self.beta = beta
        if setpoint_range is not None:
            self.setpoint_range = setpoint_range
        if p_limit is not None:
            self.p_limit = p_limit
        if i_limit is not None:
            self.i_limit = i_limit
        if d_limit is not None:
            self.d_limit = d_limit
        if delta_limit is not None:
            self.delta_limit = delta_limit
        if integral_valid is not None:
            self.integral_valid = integral_valid
        if dead_zone is not None:
            self.dead_zone = dead_zone

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

    def _serialize(self):
        """
        Serialize the Controller object.

        Returns:
            dict: A dictionary representation of the Controller object.
        """
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
            "delta_limit": [self.delta_limit, None]
            if self.delta_limit
            else [None, True],
            "integral_valid": [self.integral_valid, None]
            if self.integral_valid
            else [None, True],
            "dead_zone": [self.dead_zone, None] if self.dead_zone else [None, True],
        }

    def _serialize_selected(self, keys: List[str]) -> dict:
        """
        Serialize selected attributes of the Controller object.

        Args:
            keys (List[str]): List of attribute names to be serialized.

        Returns:
            dict: Serialized representation of selected attributes.
        """
        serialized_data = self._serialize()
        for key in list(serialized_data.keys()):
            if key not in keys:
                serialized_data.pop(key)
        return serialized_data


class ScheduleConstraints:
    """
    Class representing the schedule constraints for a Schedule.

    Attributes:
        process (Optional[Tuple[float, float]]): Process parameter schedule.
        error (Optional[Tuple[float, float]]): Error parameter schedule.
        control (Optional[Tuple[float, float]]): Control parameter schedule.

    """

    process: Optional[Tuple[float, float]]
    error: Optional[Tuple[float, float]]
    control: Optional[Tuple[float, float]]

    def __init__(
        self,
        process: Optional[Tuple[float, float]] = None,
        error: Optional[Tuple[float, float]] = None,
        control: Optional[Tuple[float, float]] = None,
    ):
        """
        Initialize the ControllerSchedule instance.

        Args:
            process (Optional[Tuple[float, float]]): Process parameter schedule.
            error (Optional[Tuple[float, float]]): Error parameter schedule.
            control (Optional[Tuple[float, float]]): Control parameter schedule.
        """
        self._init_defaults()
        valid_attributes = {
            "process": (tuple, type(None)),
            "error": (tuple, type(None)),
            "control": (tuple, type(None)),
        }

        if process is not None and not isinstance(process, valid_attributes["process"]):
            warnings.warn(f"Invalid value for process: {process}")
        else:
            self.process = process

        if error is not None and not isinstance(error, valid_attributes["error"]):
            warnings.warn(f"Invalid value for error: {error}")
        else:
            self.error = error

        if control is not None and not isinstance(control, valid_attributes["control"]):
            warnings.warn(f"Invalid value for control: {control}")
        else:
            self.control = control

    def _init_defaults(self):
        """Default initializer."""
        self.process = None
        self.error = None
        self.control = None

    def _serialize(self) -> dict:
        return self.__dict__


class Schedule:
    """
    Class representing a schedule combining a controller and its associated schedule parameters.

    Attributes:
        controller (Controller): The controller parameters.
        schedule (Optional[ControllerSchedule]): The schedule parameters for the controller.

    """

    controller: ScheduleParameters
    schedule: ScheduleConstraints
    _index: int
    _pid: "Pid"

    def __init__(
        self,
        controller: ScheduleParameters,
        schedule: Optional[ScheduleConstraints] = None,
    ):
        """
        Initialize the Schedule instance.

        Args:
            controller (Controller): The controller parameters.
            schedule (Optional[ControllerSchedule]): The schedule parameters for the controller.
                Defaults to None, in which case an empty ControllerSchedule is created.

        """
        self.controller = controller
        if schedule is None:
            schedule = ScheduleConstraints()
        self.schedule = schedule

    def _serialize(self) -> dict:
        """
        Serialize the Schedule object.

        Returns:
            dict: A dictionary representation of the Schedule object.

        """
        return {
            **self.schedule._serialize(),  # pylint: disable=protected-access
            **self.controller._serialize(),  # pylint: disable=protected-access
        }

    def _assign_index(self, index: int, pid: "Pid") -> dict:
        """
        Assign the index for the Schedule

        Returns:
            dict: A dictionary representation of the Schedule object.

        """
        self._index = index
        self._pid = pid

    def change_parameters(self, kp=None, ki=None, kd=None, bias=None):
        """
        Change the PID parameters.

        Args:
            kp (float): New proportional gain.
            ki (float): New integral gain.
            kd (float): New derivative gain.
        """
        update_keys = []

        if kp is not None:
            self.controller.kp = kp
            update_keys.append("kp")

        if ki is not None:
            self.controller.ki = ki
            update_keys.append("ki")

        if kd is not None:
            self.controller.kd = kd
            update_keys.append("kd")

        if bias is not None:
            self.controller.bias = bias
            update_keys.append("bias")

        # pylint: disable=protected-access
        update_schedule = len(self._pid._pid_controller.pid.schedule) * [None]
        # pylint: disable=protected-access
        update_schedule[self._index] = self.controller._serialize_selected(update_keys)

        update_dict = {"schedule": update_schedule}

        # pylint: disable=protected-access
        self._pid._pid_controller._update(update_dict)


class Pid:
    """
    Class representing a PID controller.

    Attributes:
        enabled (bool): Enable / Disable the PID controller. Will output None when disabled.
        update_interval_ms (int): Time interval between updates.
        setpoint (float): Ideal setpoint to strive for.
        schedule (List[Schedule]): List of Schedule instances associated with the PID controller.
        integral_term (float): Integral term for the controller.
        output_limits (Tuple[Optional[float], Optional[float]]): Limits on the controller output.

    """

    enabled: bool
    update_interval_ms: int
    setpoint: float
    schedule: List[Schedule]
    integral_term: float
    output_limits: Tuple[Optional[float], Optional[float]]
    _pid_controller: "PidController"

    def __init__(
        self,
        setpoint: float,
        update_interval_ms: int = 1000,
        **kwargs,
    ):
        """
        Initialize the PID instance.

        Args:
            setpoint (float): Ideal setpoint to strive for.
            update_interval_ms (int): Time interval between updates. Defaults to 1000 ms.
            **kwargs: Additional attributes to customize the PID instance.

        """
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
        """
        Add a Schedule instance to the PID controller.

        Args:
            schedule (Schedule): The Schedule instance to be added.

        """
        index = len(self.schedule)
        self.schedule.append(schedule)
        # pylint: disable=protected-access
        schedule._assign_index(index, self)

    def _serialize(self) -> dict:
        """
        Serialize the PID object.

        Returns:
            dict: A dictionary representation of the PID object.

        """
        return {
            "enabled": self.enabled,
            "update_interval_ms": self.update_interval_ms,
            "setpoint": self.setpoint,
            "integral_term": self.integral_term,
            "schedule": [
                # pylint: disable=protected-access
                s._serialize()
                for s in self.schedule
            ],
            "output_limits": list(self.output_limits),
        }

    def _serialize_selected(self, keys: List[str]) -> dict:
        """
        Serialize selected attributes of the Controller object.

        Args:
            keys (List[str]): List of attribute names to be serialized.

        Returns:
            dict: Serialized representation of selected attributes.
        """
        serialized_data = self._serialize()
        for key in list(serialized_data.keys()):
            if key not in keys:
                serialized_data.pop(key)
        return serialized_data

    def _assign_controller(self, controller: "PidController"):
        """
        Assign the PID Controller.
        """
        self._pid_controller = controller
        for (i, s) in enumerate(self.schedule):
            # pylint: disable=protected-access
            s._assign_index(i, self)


class PidController:
    """
    Class representing a PID controller.

    Attributes:
        name (Optional[str]): Optional name of the PID controller.
        process_value (AccessorData): Data for the process value accessor.
        control_value (AccessorData): Data for the control (manipulated) value accessor.
        pid (Pid): The PID control parameters.
        _id (int): The ID of the PID controller.
        _aq ("Aqueduct"): Internal reference to an Aqueduct instance.

    """

    def __init__(
        self,
        name: Optional[str],
        process_value: AccessorData,
        control_value: AccessorData,
        pid_params: Pid,
    ):
        """
        Initialize the PID controller.

        Args:
            name (Optional[str]): Optional name of the PID controller.
            input_data (AccessorData): Data for the input accessor.
            output_data (AccessorData): Data for the output accessor.
            pid_params (Pid): The PID control parameters.

        """
        self.name = name
        self.input = process_value
        self.output = control_value
        self.pid = pid_params

        self.pid._assign_controller(self)  # pylint: disable=protected-access

        self._id = None
        self._aq = None

    def delete(self):
        """
        Destructor method.
        """
        if self._aq is not None:
            message = json.dumps(
                [
                    SocketCommands.SocketMessage.value,
                    [
                        Events.DELETE_PID_CONTROLLERS.value,
                        dict(ids=[self._id]),
                    ],
                ]
            ).encode()

            _ok, _response = self._aq.send_and_wait_for_rx(
                message,
                Events.DELETED_PID_CONTROLLERS.value,
                SOCKET_TX_ATTEMPTS,
            )

    def _assign(self, aqueduct: "Aqueduct"):
        """
        Set an Aqueduct instance for this PID controller.

        Args:
            aqueduct (Aqueduct): An instance of Aqueduct.
        """
        self._aq = aqueduct
        # pylint: disable=protected-access
        self.pid._assign_controller(self)

    def _set_id(self, controller_id: int):
        """
        Set the ID for this PID controller.

        Args:
            controller_id (int): The ID of the PID controller.

        """
        self._id = controller_id

    def _serialize(self) -> dict:
        """
        Serialize the PID controller object.

        Returns:
            dict: a dictionary representation of the PID controller object
        """
        return {
            "name": self.name,
            "input": self.input._serialize(),  # pylint: disable=protected-access
            "output": self.output._serialize(),  # pylint: disable=protected-access
            "pid": self.pid._serialize(),  # pylint: disable=protected-access
        }

    def _serialize_update(self, pid: dict) -> dict:
        """
        Serialize the PID controller object for update.

        Returns:
            dict: A dictionary representation of the PID controller object.

        """
        return {
            "id": self._id,
            "pid": pid,
        }

    def change_setpoint(self, setpoint: float, clear_integral: bool = False):
        """
        Change the setpoint of the PID controller.
        """
        update_keys = ["setpoint"]
        self.pid.setpoint = setpoint

        if clear_integral:
            self.pid.integral_term = 0.0
            update_keys.append("integral_term")

        # pylint: disable=protected-access
        self._update(self.pid._serialize_selected(update_keys))

    def enable(self):
        """
        Enable the PID controller.
        """
        update_keys = ["enabled"]
        self.pid.enabled = True

        # pylint: disable=protected-access
        self._update(self.pid._serialize_selected(update_keys))

    def disable(self):
        """
        Disable the PID controller.
        """
        update_keys = ["enabled"]
        self.pid.enabled = False

        # pylint: disable=protected-access
        self._update(self.pid._serialize_selected(update_keys))

    def clear_integral(self):
        """
        Clear the integral term of the PID controller.
        """
        update_keys = ["integral_term"]
        self.pid.integral_term = 0.0

        # pylint: disable=protected-access
        self._update(self.pid._serialize_selected(update_keys))

    def _update(self, pid: dict):
        message = json.dumps(
            [
                SocketCommands.SocketMessage.value,
                [
                    Events.UPDATE_PID_CONTROLLERS.value,
                    dict(controllers=[self._serialize_update(pid)]),
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
