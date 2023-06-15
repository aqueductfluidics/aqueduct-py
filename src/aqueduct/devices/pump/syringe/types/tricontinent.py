import enum
from typing import Union


class PumpSeries(enum.IntEnum):
    """
    Enum representing the series of a pump.

    The available pump series are:
    - CX6000
    - CX48000
    - C3000
    - C24000
    """

    CX6000 = 0
    CX48000 = 1
    C3000 = 2
    C24000 = 3


# pylint: disable=invalid-name
class Booted(enum.IntEnum):
    """
    Enum representing the `Booted` status of a pump.

    The available statuses are:
    - Missing
    - Booted
    """

    Missing = 0
    Booted = 1


# pylint: disable=invalid-name
class CSeriesError(enum.IntEnum):
    """
    Enum representing the error status of a pump.

    The available error statuses are:
    - NoError
    - InitializationFailure
    - InvalidCommand
    - InvalidOperand
    - InvalidChecksum
    - Unused
    - EepromFailure
    - DeviceNotInitialized
    - CanBusFailure
    - PlungerOverload
    - ValveOverload
    - PlungerNotAllowed
    - CommandOverflow
    """

    NoError = 0b00000
    InitializationFailure = 0b00001
    InvalidCommand = 0b00010
    InvalidOperand = 0b00011
    InvalidChecksum = 0b00100
    Unused = 0b00101
    EepromFailure = 0b00110
    DeviceNotInitialized = 0b00111
    CanBusFailure = 0b01000
    PlungerOverload = 0b01001
    ValveOverload = 0b01010
    PlungerNotAllowed = 0b01011
    CommandOverflow = 0b01111


class TriContinentConfigKeys(enum.Enum):
    """
    Enum representing the keys of TriContinentConfig.
    """

    Booted = "booted"
    CSeriesError = "c_series_error"
    PumpSeries = "pump_series"
    Initialized = "initialized"


class TriContinentConfig:
    """
    Configuration data for a TriContinent pump.

    :param booted: The `Booted` status of the pump.
    :type booted: int
    :param c_series_error: The error status of the pump.
    :type c_series_error: int
    :param pump_series: The series of the pump.
    :type pump_series: int
    """

    def __init__(
        self,
        booted: int,
        c_series_error: int,
        pump_series: int,
        initialized: int,
        **_kwargs
    ):

        self.booted = Booted(booted)
        self.c_series_error = CSeriesError(c_series_error)
        self.pump_series = PumpSeries(pump_series)
        self.initialized = initialized

    @classmethod
    def from_config(cls, **data) -> "TriContinentConfig":
        """
        Create a `TriContinentConfig` instance from a configuration dictionary.

        :param data: Configuration data.
        :type data: dict
        :return: The created `TriContinentConfig` instance.
        :rtype: TriContinentConfig
        """
        return TriContinentConfig(**data)


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
