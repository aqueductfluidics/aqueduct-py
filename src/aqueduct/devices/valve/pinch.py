"""PinchValve Module."""

from typing import List, Union, Tuple

import aqueduct.devices.base.obj
from aqueduct.core.socket_constants import Actions


class SetPositionCommand(object):
    pct_open: float

    def __init__(self, pct_open: float):
        self.pct_open = pct_open

    def to_command(self):
        return self.pct_open


class PinchValve(aqueduct.devices.base.obj.Device):
    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)

    def set_position(
        self,
        commands: List[Union[SetPositionCommand, None]],
        record: Union[bool, None] = None,
    ) -> dict:
        """Command to set the position of one or more pinch valve inputs.

        :Example:

        .. code-block:: python

            commands = pinch_valve.make_commands()
            command = pinch_valve.make_start_command(
                mode=pinch_valve.MODE.Continuous, 
                rate_units=pinch_valve.RATE_UNITS.MlMin,
                rate_value=2, 
                direction=pinch_valve.STATUS.Clockwise)
            pinch_valve.set_command(commands, 0, command)
            pinch_valve.start(commands)

        :param commands: List[Union[StartCommand, None]]

        :return: None
        :rtype: None
        """
        commands = [c.to_command() for c in commands]
        payload = self.to_payload(
            Actions.SetValvePosition,
            {"commands": commands},
            record
        )
        self.send_command(payload)

    def set_command(
        self,
        commands: List[Union[SetPositionCommand, None]],
        index: int,
        command: SetPositionCommand,
    ):
        """Helper method to create an instance of a :class:`pinch_valveCommand`.

        A :class:`pinch_valveCommand` is an object with the required fields to set the operation
        parameters for a pinch_valve input.

        :return: pinch_valve_command
        :rtype: pinch_valveCommand
        """
        if index < len(commands):
            commands[index] = command
        else:
            raise Warning(
                "Peristalticpinch_valve: command index larger than device size!")

    @staticmethod
    def make_set_poisition_command(
        pct_open: float
    ) -> SetPositionCommand:
        """Helper method to create an instance of a :class:`pinch_valveCommand`.

        A :class:`pinch_valveCommand` is an object with the required fields to set the operation
        parameters for a pinch_valve input.

        :return: pinch_valve_command
        :rtype: pinch_valveCommand
        """
        return SetPositionCommand(pct_open=pct_open)

    def get_pct_open(self) -> Tuple[float]:
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
            values.append(ipt.get('p'))
        return tuple(values)
