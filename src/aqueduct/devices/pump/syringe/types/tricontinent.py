import enum
from typing import Union


class PumpSeries(enum.IntEnum):
    """
    Enum representing the series of a pump.
    """

    CX6000 = 0
    CX48000 = 1
    C3000 = 2
    C24000 = 3


def min_rate_ul_min(
    pump_series: int, resolution: int, syringe_volume_ul: float
) -> Union[float, None]:
    """
    Calculate the minimum flow rate in microliters per minute based on the pump series, resolution, and syringe volume.

    :param pump_series: The pump series value.
    :type pump_series: int
    :param resolution: The resolution value.
    :type resolution: int
    :param syringe_volume_ul: The syringe volume in microliters.
    :type syringe_volume_ul: float
    :return: The minimum flow rate in microliters per minute, or None if the pump series is not supported.
    :rtype: Union[float, None]
    """
    if pump_series == PumpSeries.C3000.value:
        if resolution in (0, 1):
            return syringe_volume_ul / 6000.0 * 60
        elif resolution in (2,):
            return syringe_volume_ul / 48000.0 * 60
    elif pump_series == PumpSeries.C24000.value:
        if resolution in (0, 1):
            return syringe_volume_ul / 24000.0 * 60
        elif resolution in (2,):
            return syringe_volume_ul / 192000.0 * 60
    return None


def max_rate_ul_min(
    pump_series: int, resolution: int, syringe_volume_ul: float
) -> Union[float, None]:
    """
    Calculate the maximum flow rate in microliters per minute based on the pump series, resolution, and syringe volume.

    :param pump_series: The pump series value.
    :type pump_series: int
    :param resolution: The resolution value.
    :type resolution: int
    :param syringe_volume_ul: The syringe volume in microliters.
    :type syringe_volume_ul: float
    :return: The maximum flow rate in microliters per minute, or None if the pump series is not supported.
    :rtype: Union[float, None]
    """
    value = min_rate_ul_min(pump_series, resolution, syringe_volume_ul)
    if value is not None:
        value *= 6000
    return value
