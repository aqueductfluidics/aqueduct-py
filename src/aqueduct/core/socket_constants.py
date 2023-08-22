"""
This module provides an interface for interacting with the Aqueduct server.

The `Aqueduct` class is used to connect to an Aqueduct server and send commands to its devices.
The `SocketCommands` and `Events` enums provide constants for identifying socket commands and events.
The `Actions` enum provides constants for identifying device actions.
"""
import enum

SOCKET_DELAY_S = 0.005
SOCKET_TX_ATTEMPTS = 3

OK = "ok"


class SocketCommands(enum.IntEnum):
    """Enumeration for socket commands."""

    RegisterUser = 0
    RegisterEvents = 1
    SocketMessage = 2


class Events(enum.Enum):
    """Enumeration for events."""

    ADD_DEVICE = "add_device"
    CREATE_PID_CONTROLLERS = "create_pid_controllers"
    CREATED_PID_CONTROLLERS = "created_pid_controllers"
    CLEAR_DEVICE_RECORDABLE = "clear_device_recordable"
    CLEAR_SETUP = "clear_setup"
    CLEAR_USER_RECORDABLES = "clear_user_recordables"
    DELETE_PID_CONTROLLERS = "delete_pid_controllers"
    DELETED_PID_CONTROLLERS = "delete_pid_controllers"
    DEVICE_ACTION = "device_action"
    GET_DEVICE = "get_device"
    GET_DEVICE_LIVE = "get_device_live"
    GET_RECIPE_INPUT = "get_recipe_input"
    GET_RECIPE_INPUT_VALUE = "get_recipe_input_value"
    GET_RECIPE_PROMPT = "get_recipe_prompt"
    GET_SETUP = "get_setup"
    PAUSE_RECIPE = "pause_recipe"
    RECIPE_STATUS = "recipe_status"
    REGISTER_PROCESS = "register_process"
    REGISTERED_USER = "registered_user"
    SET_RECIPE_INPUT = "set_recipe_input"
    SET_RECIPE_PROMPT = "set_recipe_prompt"
    UPDATE_PID_CONTROLLERS = "update_pid_controllers"
    UPDATED_PID_CONTROLLERS = "updated_pid_controllers"
    UPDATE_PROCESS = "update_process"
    UPDATE_USER_PARAMS = "update_user_params"
    UPDATE_USER_RECORDABLES = "update_user_recordables"
    UPDATED_USER_PARAMS = "updated_user_params"


class Actions(enum.IntEnum):
    """Enumeration for device actions."""

    SetConfig = 0
    SetSimValues = 1
    UpdateRecord = 2
    Start = 3
    Stop = 4
    ChangeSpeed = 5
    SetValvePosition = 6
    Tare = 7
    SetCalibration = 8
    Initialize = 9
    SetPlunger = 10
    Zero = 11
