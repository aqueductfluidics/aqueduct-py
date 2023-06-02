import json
import time
from typing import Union

from aqueduct.core.socket_constants import Events
from aqueduct.core.socket_constants import SocketCommands
from aqueduct.core.utils import send_and_wait_for_rx


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
    pause_recipe = False

    _delay_s = 0.5
    _aq: "aqueduct.core.aq.Aqueduct"

    def __init__(
        self, message: str, timeout_s: Union[int, str], pause_recipe: Union[bool, None]
    ):
        """
        Constructor method.
        """
        if pause_recipe is None:
            pause_recipe = False

        self.start_time = time.monotonic_ns()
        self.message = message
        self.timeout_s = timeout_s
        self.pause_recipe = pause_recipe

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

            _, data = send_and_wait_for_rx(
                message=message,
                sock=self._aq.socket,
                lock=self._aq.socket_lock,
                response=Events.GET_RECIPE_PROMPT.value,
            )

            try:
                i = json.loads(data)
                if i.get("prompt"):
                    return True
            except json.decoder.JSONDecodeError:
                if data == "ack":
                    return False

    def serialize(self):
        """
        Returns a dictionary of the prompt object.

        Returns:
            dict: a dictionary of the prompt object.
        """
        return dict(
            message=self.message,
            timeout_s=self.timeout_s,
            start_time=self.start_time,
            pause_recipe=self.pause_recipe,
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
