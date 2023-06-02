"""
This module provides a class for logging timestamped data.

Classes:
    Recordable: A class to provide logging functionality for timestamped data.
"""
import datetime
import json
from typing import Union

ALLOWED_DTYPES = (
    int.__name__,
    float.__name__,
    bool.__name__,
    list.__name__,
    datetime.__name__,
    str.__name__,
)


class Recordable:
    """
    The `Recordable` class allows you to log timestamped data.

    :param name: Name of the recordable, will be displayed on the UI, should be unique
    :type name: str, required
    :param value: Initial value to be assigned to the recordable on creation
    :type value: float, int, bool, str, datetime.datetime, list, required
    :param dtype: Specify the type of value, used to ensure that users cannot
        enter an invalid value
    :type dtype: {'int', 'float', 'bool', 'list', 'datetime', 'str'}, optional
    """

    name: str = None
    value: Union[float, int, bool, str, datetime.datetime, list] = None
    dtype: str = None
    timestamp = None

    _aq: "Aqueduct" = None

    def __init__(
        self,
        name: str,
        value: Union[float, int, bool, str, datetime.datetime, list],
        dtype: str = None,
    ):
        """
        Constructor method.

        :param name: name of the Recordable, will be displayed on the UI, should be unique
        :type name: str, required
        :param value: value to be assigned to the Recordable on creation
        :type value: float, int, bool, str, datetime.datetime, list, required
        :param dtype: specify the type of value, used to ensure that users cannot enter an invalid value
        :type dtype: {'int', 'float', 'bool', 'list', 'datetime', 'str'}, optional
        """
        if dtype is None:
            try:
                dtype = type(value).__name__
                if dtype not in ALLOWED_DTYPES:
                    raise ValueError(
                        "Object of type {} is not allowed as a Recordable".format(
                            {dtype}
                        )
                    )
            except Exception:
                raise ValueError("Invalid Aqueduct Recordable")

        self.name = name
        self.value = value
        self.dtype = dtype

    def __del__(self):
        """
        Destructor method.
        """
        if self._aq is not None:
            try:
                self._aq.remove_recordable(self)
            except KeyError:
                pass

    def assign(self, aqueduct: "Aqueduct"):
        """
        Assigns the Recordable to an `Aqueduct` instance.

        :param aqueduct: The `Aqueduct` instance to assign the Recordable to.
        :type aqueduct: Aqueduct, required
        """
        self._aq = aqueduct

    def serialize(self):
        """
        Serializes the Recordable into a dictionary for JSON serialization.

        :return: Dictionary representing the Recordable.
        """
        return dict(n=self.name, v=self.value, d=self.dtype)

    def update(self, value):
        """
        Updates the value of the Recordable.

        :param value: The new value for the Recordable.
        :type value: Union[float, int, bool, str, datetime.datetime, list], required
        """
        self.value = value
        self._aq.update_recordable(self)

    def clear(self):
        """
        Clears the value of the Recordable.
        """
        self._aq.clear_recordable(self)

    def to_json(self):
        """Return a JSON representation of the recordable"""
        return json.dumps(self, default=lambda o: o.serialize())
