from typing import List, Tuple, Union

import aqueduct.devices.base.obj


class TestDevice(aqueduct.devices.base.obj.Device):
    def __init__(self, socket, socket_lock, **kwargs):
        super().__init__(socket, socket_lock, **kwargs)

    def set_roc(self, roc: List[int], record: Union[None, bool] = None):
        """
        :param roc:
        :type roc: List[int]
        :param record: record the data from each balance
        :type record: bool

        :return: command dictionary
        :rtype: dict
        """
        payload = self.to_payload(0x10000, {"commands": roc}, record)
        self.send_command(payload)

    def get_value(self, index: int = 0) -> int:
        """

        :param index: input to read from, `0` is first input
        :type index: int, {0:1}
        :return: value
        :rtype: float, None
        """
        return self.get_all_values()[index]

    def get_all_values(self) -> Tuple[int]:
        """

        :return: weight values
        :rtype: list
        """
        data = self.get()
        values = []
        for i in range(0, self.len):
            ipt = data.get("live")[i]
            values.append(ipt.get("v"))
        return tuple(values)
