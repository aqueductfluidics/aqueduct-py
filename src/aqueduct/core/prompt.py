import json
import time
from typing import Union

from aqueduct.core.socket_constants import (
    SOCKET_DELAY_S,
    Events,
    SocketCommands,
)


class Prompt:
    """
    A class to provide simple creation of User Prompts.

    Args:
        message (str): string to flash in the Message
        timeout_s (Union[int, str, None], optional): the length of time in seconds before the Recipe
            resumes execution if the Input has not been executed, set to None
            or leave blank to disable a time-out, should be number-like

    Attributes:
        message (str): string to flash in the Message
        timeout_s (Union[int, str, None]): the length of time in seconds before the Recipe
            resumes execution if the Input has not been executed, set to None
            or leave blank to disable a time-out, should be number-like
        start_time (float): the start time of the prompt in nanoseconds
        _delay_s (float): internal delay value
        _aq (aqueduct.core.aq.Aqueduct): the aqueduct instance to use

    Methods:
        __bool__: Override the built-in truth value testing.
            A prompt will return `True` when a truthiness test is performed
            until it has been dismissed by a User.

        serialize: Returns a dictionary of the prompt object.

        assign: Assigns the Aqueduct instance to the prompt.

        to_json: Returns the prompt object as a JSON string.


    """

    message = None
    timeout_s = None
    start_time = None

    _delay_s = 0.5
    _aq: "aqueduct.core.aq.Aqueduct"

    def __init__(self, message: str, timeout_s: Union[int, str]):
        """
        Constructor method.
        """
        self.start_time = time.monotonic_ns()
        self.message = message
        self.timeout_s = timeout_s

    def __bool__(self):
        """
        Override the built-in truth value testing.

        A prompt will return `True` when a truthiness
        test is performed until it has been dismissed by a
        User.

        Returns:
            bool: True if the prompt has not been dismissed, False otherwise.
        """
        time.sleep(self._delay_s)
        if self._aq:
            message = json.dumps(
                [
                    SocketCommands.SocketMessage.value,
                    [
                        Events.GET_RECIPE_PROMPT.value,
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
            if j[0] == Events.GET_RECIPE_PROMPT.value:
                try:
                    i = json.loads(j[1])
                    if i.get("prompt"):
                        return True
                except json.decoder.JSONDecodeError:
                    if j[1] == "ack":
                        return False

    def serialize(self):
        """
        Returns a dictionary of the prompt object.

        Returns:
            dict: a dictionary of the prompt object.
        """
        return dict(
            message=self.message, timeout_s=self.timeout_s, start_time=self.start_time
        )

    def assign(self, aq: "aqueduct.core.aq.Aqueduct"):
        """
        Assign an instance of the Aqueduct class to the prompt.

        Args:
            aq (aqueduct.core.aq.Aqueduct): The instance of the Aqueduct class to assign.
        """
        self._aq = aq

    def to_json(self):
        """
        Returns a JSON string representation of the `Prompt` object.

        :return: A JSON string representation of the `Prompt` object.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.serialize())
