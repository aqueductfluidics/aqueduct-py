import json
import time
from enum import Enum
from typing import Union


from aqueduct.core.socket_constants import (
    SOCKET_DELAY_S,
    Events,
    SocketCommands,
)


class UserInputTypes(Enum):
    """
    Enumeration of supported User Input types.

    Attributes:
        DROPDOWN: A User Input type representing a dropdown menu.
        TEXT_INPUT: A User Input type representing a text input field.
        BUTTONS: A User Input type representing a set of buttons.
        TABLE: A User Input type representing a table.
        CSV_UPLOAD: A User Input type representing a CSV file upload field.
    """
    DROPDOWN = "dropdown"
    TEXT_INPUT = "text_input"
    BUTTONS = "buttons"
    TABLE = "table"
    CSV_UPLOAD = "csv"


class Input(object):
    """
    A class to provide simple creation of User Inputs.

    Args:
        message (str): The message to display to the user.
        timeout_s (Union[int, str]): The length of time in seconds before the Recipe
            resumes execution if the Input has not been executed. Set to None
            or leave blank to disable a time-out. Should be number-like.

        input_type (str, optional): The type of input to create, one of UserInputTypes. 
            Defaults to UserInputTypes.TEXT_INPUT.value.
        options (list, optional): A list of options for a dropdown or button input type. 
            Defaults to None.
        rows (list, optional): A list of rows to display in a table input type. 
            Defaults to None.
        dtype (str, optional): The data type of the input value. One of {'int', 'float', 'bool', 
            'list', 'datetime', 'str'}. Defaults to None.

    Attributes:
        message (str): The message to display to the user.
        timeout_s (Union[int, str]): The length of time in seconds before the Recipe
            resumes execution if the Input has not been executed. Set to None
            or leave blank to disable a time-out. Should be number-like.
        start_time: The time when the input was created.
        input_type (str): The type of input to create, one of UserInputTypes.
        options (list): A list of options for a dropdown or button input type.
        rows (list): A list of rows to display in a table input type.
        dtype (str): The data type of the input value. One of {'int', 'float', 'bool', 
            'list', 'datetime', 'str'}.

    """
    message = None
    timeout_s = None
    start_time = None
    input_type = None
    options = []
    rows = []
    dtype = None

    _delay_s = 0.5
    _aq: "aqueduct.core.aq.Aqueduct"

    def __init__(
        self,
        message: str,
        timeout_s: Union[int, str],
        input_type: str = UserInputTypes.TEXT_INPUT.value,
        options: list = None,
        rows: list = None,
        dtype: str = None,
    ):
        """
        Constructor method.
        """
        if options is None:
            options = []

        if rows is None:
            rows = []

        self.start_time = time.monotonic_ns()
        self.message = message
        self.timeout_s = timeout_s
        self.input_type = input_type
        self.options = options
        self.rows = rows
        self.dtype = dtype

    def __bool__(self):
        """
        A prompt will return `True` when a truthiness
        test is performed until it has been dismissed by a
        User.

        :return: None
        """
        time.sleep(self._delay_s)
        if self.is_set():
            return True
        else:
            return False

    def assign(self, aq: "aqueduct.core.aq.Aqueduct"):
        """
        Assigns the specified Aqueduct instance to the Input instance.

        :param aq: The Aqueduct instance to assign to the Input instance.
        :type aq: aqueduct.core.aq.Aqueduct
        :return: None
        """
        self._aq = aq

    def serialize(self):
        """
        Returns the Input instance as a serialized dictionary.

        :return: The serialized dictionary representing the Input instance.
        :rtype: dict
        """
        return dict(
            message=self.message,
            timeout_s=self.timeout_s,
            start_time=self.start_time,
            input_type=self.input_type,
            options=self.options,
            rows=self.rows,
            dtype=self.dtype,
        )

    def is_set(self) -> bool:
        """
        Returns True if the Input has been set by the user, False otherwise.

        :return: True if the Input has been set by the user, False otherwise.
        :rtype: bool
        """
        if self._aq:
            message = json.dumps(
                [
                    SocketCommands.SocketMessage.value,
                    [
                        Events.GET_RECIPE_INPUT.value,
                        dict(user_id=self._aq.user_id),
                    ],
                ]
            ).encode()
            self._aq.socket.settimeout(1)
            with self._aq.socket_lock:
                self._aq.socket.send(message)
                time.sleep(SOCKET_DELAY_S)
            data = self._aq.socket.recv(1024 * 8)
            j = json.loads(data)
            if j[0] == Events.GET_RECIPE_INPUT.value:
                i = json.loads(j[1])
                if i.get("input").get("value"):
                    return True
            return False

    def get_value(self, delete_if_set: bool = True):
        """
        Read the value from the user input.

        If `delete_if_set` is set to `True`, will delete the input upon readout
        if the Input has been executed.

        :param delete_if_set:
        :type delete_if_set: bool, defaults to True
        :return: Input's value
        :rtype: {'int', 'float', 'bool', 'list', 'datetime', 'str'}
        """
        if self._aq:
            message = json.dumps(
                [
                    SocketCommands.SocketMessage.value,
                    [
                        Events.GET_RECIPE_INPUT_VALUE.value,
                        dict(user_id=self._aq.user_id),
                    ],
                ]
            ).encode()
            self._aq.socket.settimeout(1)
            with self._aq.socket_lock:
                self._aq.socket.send(message)

            i = 0
            while True:
                data = self._aq.socket.recv(1024 * 8)
                try:
                    j = json.loads(data)
                    if j[0] == Events.GET_RECIPE_INPUT_VALUE.value:
                        v = json.loads(j[1])
                        v = v.get("value")
                        if self.dtype == float.__name__:
                            return float(v)
                        elif self.dtype == int.__name__:
                            return int(v)
                        else:
                            return v
                except BaseException as _e:
                    continue
                i += 1
                if i > 10:
                    break

            return None

    def to_json(self):
        """
        Return a JSON representation of the Input object.

        :return: A JSON-encoded string representation of the Input object.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.serialize())
