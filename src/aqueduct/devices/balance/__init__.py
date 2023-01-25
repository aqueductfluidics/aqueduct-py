"""
The `Balance` class represents a balance device in the Aqueduct Fluidics 
ecosystem. The `Balance` class inherits from the base `Device` class and 
provides methods to interact with and control the balance device.

Example usage:

    # initialize the Aqueduct core application and the balance device
    aq = Aqueduct(user_id, ip_address, port)
    balance = aq.devices.get("balance")

    # tare the balance
    balance.tare()

    # get a weight reading from the balance
    weight = balance.get_value()

    # get all weight readings from the balance
    weights = balance.get_all_values()

"""
from typing import Tuple, Union

import aqueduct.devices.base.obj
from aqueduct.core.socket_constants import Actions


class Balance(aqueduct.devices.base.obj.Device):
    """Class representing a balance device.

    This class represents a balance device, which can be used to weigh substances. Methods are provided
    to tare the device, read a weight value, and read all weight values.

    :ivar has_sim_values: Flag indicating whether the device has simulated values.
    :type has_sim_values: bool
    """

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    def tare(self, index: int = 0, record: Union[bool, None] = None):
        """
        Send a tare command to the balance device.

        :param index: number-like value to specify the input of the balance to tare
        :type index: int
        """
        commands = self.len * [None]
        commands[index] = 1

        payload = self.to_payload(
            Actions.Tare,
            {"commands": commands},
            record
        )
        self.send_command(payload)

    def value(self, index: int = 0):
        """
        Get a weight value reading from the balance device.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in grams
        :rtype: float or None
        """

        live = self.get_live()
        return live[index].get('g')

    def get_value(self, index: int = 0):
        """
        Alias for the `value` method.

        :param index: input to read from, `0` is first input
        :type index: int
        :return: value, in grams
        :rtype: float or None
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the weight readings from a balance device.

        :return: weight values for all inputs
        :rtype: tuple of floats
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            values.append(ipt.get('g'))
        return tuple(values)
