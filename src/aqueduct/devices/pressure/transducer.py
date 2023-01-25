from typing import Tuple, Union

import aqueduct.devices.base.obj
from aqueduct.core.socket_constants import Actions


class PressureTransducer(aqueduct.devices.base.obj.Device):

    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)
        self.has_sim_values = True

    def tare(self, index: int = 0, record: Union[bool, None] = None):
        """Send a tare command to one of the balance inputs.

        :Example: tare input 1 of the :class:`Balance` device named `balance`:

        .. code-block:: python

            balance.tare(input=1)

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
        Get a weight value reading from one of the balance inputs. The *input_num* argument
        selects the input channel to read.

        If no valid input is present or the weight reading is invalid, returns `None`.

        :Example: read weight from input 0:

        .. code-block:: python

            balance.value(0)

        :Example: read weight from input 3:

        .. code-block:: python

            balance.value(3)

        :param index: input to read from, `0` is first input
        :type index: int, {0:2}
        :return: value, in weight
        :rtype: float, None
        """
        live = self.get_live()
        return live[index].get('v')

    def get_value(self, index: int = 0):
        """
        Alias for the py:func:`value` method.

        :Example: read weight from input 3:

        .. code-block:: python

            balance.get_value(3)

        :param index: input to read from, `0` is first input
        :type index: int, {0:2}
        :return: value, in grams
        :rtype: float, None
        """
        return self.value(index)

    def get_all_values(self) -> Tuple[float]:
        """
        Get all of the weight readings from a Balance device.

        :Example: read all balances:

        .. code-block:: python

            weight_values = balance.get_all_values()
            len(weights) # == balance.len

        :return: weight values
        :rtype: list
        """
        live = self.get_live()
        values = []
        for i in range(0, self.len):
            ipt = live[i]
            values.append(ipt.get('v'))
        return tuple(values)





