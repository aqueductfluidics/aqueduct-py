"""
This module provides a class for simple interaction with Recipe values that appear
as User Params on the Aqueduct Recipe Builder UI.

Classes:
    Setpoint: A class to provide simple interaction with Recipe values that appear as
        User Params on the Aqueduct Recipe Builder UI.

"""
import datetime
import json
from typing import Callable
from typing import Union

ALLOWED_DTYPES = (
    int.__name__,
    float.__name__,
    bool.__name__,
    list.__name__,
    datetime.__name__,
    str.__name__,
)


class Setpoint:
    """
    A class to provide simple interaction with Recipe values that
    appear as User Params on the Aqueduct Recipe Builder UI.

    Args:
        name (str): name of the Setpoint, will be displayed on the UI, should be unique
        value (Union[float, int, bool, str, datetime.datetime, list]): value to be assigned to the Setpoint on creating
        dtype ({'int', 'float', 'bool', 'list', 'datetime', 'str'}, optional): specify the type of value, used to ensure
            that Users cannot enter an invalid value

    Attributes:
        name (str): name of the Setpoint, will be displayed on the UI, should be unique
        value (Union[float, int, bool, str, datetime.datetime, list]): value of the Setpoint
        dtype (str): specify the type of value, used to ensure that Users cannot enter an invalid value
        timestamp (datetime.datetime): timestamp when the Setpoint is updated
        on_change (Callable): a function that is called when the Setpoint is updated
        args (list): arguments to pass to the `on_change` function
        kwargs (dict): keyword arguments to pass to the `on_change` function
        _aq (Aqueduct): reference to the Aqueduct object to allow for easy updating of the Setpoint

    """

    name: str = None
    value: Union[float, int, bool, str, datetime.datetime, list] = None
    dtype: str = None
    timestamp = None
    on_change: Callable = None
    args: list = []
    kwargs: dict = {}

    _aq: "Aqueduct" = None

    def __init__(
        self,
        name: str,
        value: Union[float, int, bool, str, datetime.datetime, list],
        dtype: str = None,
    ):
        """
        Constructor method.
        """

        if dtype is None:
            try:
                dtype = type(value).__name__
                if dtype not in ALLOWED_DTYPES:
                    raise ValueError(
                        "Object of type {} is not allowed as a Setpoint".format({dtype})
                    )
            except Exception:
                raise ValueError("Invalid Aqueduct Setpoint")

        self.name = name
        self.value = value
        self.dtype = dtype

    def __del__(self):
        """
        Destructor method.
        """
        if self._aq is not None:
            try:
                self._aq.remove_setpoint(self)
            except KeyError:
                pass

    def assign(self, aqueduct: "Aqueduct"):
        """
        Assign the Aqueduct object reference to the Setpoint object.

        Args:
            aqueduct (Aqueduct): Aqueduct object to be assigned

        Returns:
            None
        """
        self._aq = aqueduct

    def serialize(self):
        """
        Serialize the Setpoint object.

        Returns:
            dict: a dictionary representation of the Setpoint object
        """
        return dict(n=self.name, v=self.value, d=self.dtype)

    def update(self, value):
        """
        Update the value of this Setpoint object.

        :param value: The new value to set for the Setpoint.
        :type value: float, int, bool, str, datetime.datetime, list, required

        :return: None
        """
        self.value = value
        self._aq.update_setpoint(self)

    def to_json(self):
        """
        Convert this Setpoint object to a JSON string representation.

        :return: A JSON string representing the Setpoint object.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.serialize())
