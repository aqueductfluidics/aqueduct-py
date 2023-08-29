from enum import Enum
from typing import Tuple
from typing import Union


class PressureUnits(Enum):
    """
    Enumeration of pressure units.
    """

    TORR = 0
    PSI = 1
    ATMOSPHERE_STD = 2
    PASCAL = 3
    BAR = 4


def get_pressure_conversion(
    from_unit: PressureUnits, to_unit: PressureUnits
) -> Tuple[Union[float, None]]:
    """
    Retrieves the conversion factor between two pressure units.

    :param from_unit: The source pressure unit.
    :type from_unit: PressureUnits
    :param to_unit: The target pressure unit.
    :type to_unit: PressureUnits
    :return: The conversion factor from the source unit to the target unit.
    :rtype: Union[float, None]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion_factors = {
        (PressureUnits.TORR, PressureUnits.TORR): 1.0,
        (PressureUnits.TORR, PressureUnits.PSI): 0.0193367758,
        (PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD): 0.00131578947,
        (PressureUnits.TORR, PressureUnits.PASCAL): 133.322368,
        (PressureUnits.TORR, PressureUnits.BAR): 0.00133322368,
    }

    conversion_key = (from_unit, to_unit)
    conversion_factor = conversion_factors.get(conversion_key)

    if conversion_factor is None:
        raise ValueError(
            f"Conversion from {from_unit.value} to {to_unit.value} is not supported."
        )

    return conversion_factor


def convert_pressure_values(
    values: Tuple[Union[float, None]], from_unit: PressureUnits, to_unit: PressureUnits
) -> Tuple[Union[float, None]]:
    """
    Converts pressure values from one unit to another.

    :param values: The pressure values to be converted.
    :type values: Tuple[Union[float, None]]
    :param from_unit: The unit of the input pressure values.
    :type from_unit: PressureUnits
    :param to_unit: The desired unit for the converted pressure values.
    :type to_unit: PressureUnits
    :return: The converted pressure values.
    :rtype: Tuple[Union[float, None]]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    converted_values = [
        value * get_pressure_conversion(from_unit, to_unit)
        if value is not None
        else None
        for value in values
    ]
    return tuple(converted_values)


class WeightUnits(Enum):
    """
    Enumeration of weight units.
    """

    GRAMS = 0
    OUNCES = 1
    POUNDS = 2
    CARATS = 3
    KILOGRAMS = 4
    NEWTONS = 5


def get_weight_conversion(
    from_unit: PressureUnits, to_unit: PressureUnits
) -> Tuple[Union[float, None]]:
    """
    Retrieves the conversion factor between two weight units.

    :param from_unit: The source weight unit.
    :type from_unit: WeightUnits
    :param to_unit: The target weight unit.
    :type to_unit: WeightUnits
    :return: The conversion factor from the source unit to the target unit.
    :rtype: Union[float, None]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion_factors = {
        (WeightUnits.GRAMS, WeightUnits.GRAMS): 1.0,
        (WeightUnits.GRAMS, WeightUnits.OUNCES): 0.03527396,
        (WeightUnits.GRAMS, WeightUnits.POUNDS): 0.00220462,
        (WeightUnits.GRAMS, WeightUnits.CARATS): 5.0,
        (WeightUnits.GRAMS, WeightUnits.KILOGRAMS): 0.001,
        (WeightUnits.GRAMS, WeightUnits.NEWTONS): 0.00980665,
    }

    conversion_key = (from_unit, to_unit)
    conversion_factor = conversion_factors.get(conversion_key)

    if conversion_factor is None:
        raise ValueError(
            f"Conversion from {from_unit.value} to {to_unit.value} is not supported."
        )

    return conversion_factor


def convert_weight_values(
    values: Tuple[Union[float, None]], from_unit: WeightUnits, to_unit: WeightUnits
) -> Tuple[Union[float, None]]:
    """
    Converts weight values from one unit to another.

    :param values: The weight values to be converted.
    :type values: Tuple[Union[float, None]]
    :param from_unit: The unit of the input weight values.
    :type from_unit: WeightUnits
    :param to_unit: The desired unit for the converted weight values.
    :type to_unit: WeightUnits
    :return: The converted weight values.
    :rtype: Tuple[Union[float, None]]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    converted_values = [
        value * get_weight_conversion(from_unit, to_unit) if value is not None else None
        for value in values
    ]
    return tuple(converted_values)


class TemperatureUnits(Enum):
    """
    Enumeration of temperature units.
    """

    CELSIUS = 0
    FAHRENHEIT = 1
    KELVIN = 2


def get_temperature_conversion(
    from_unit: TemperatureUnits, to_unit: TemperatureUnits
) -> Tuple[Union[float, None]]:
    """
    Retrieves the conversion factors between two temperature units.

    :param from_unit: The source temperature unit.
    :type from_unit: TemperatureUnits
    :param to_unit: The target temperature unit.
    :type to_unit: TemperatureUnits
    :return: The conversion factors from the source unit to the target unit.
    :rtype: Tuple[Union[float, None]]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion_factors = {
        (TemperatureUnits.CELSIUS, TemperatureUnits.CELSIUS): (1.0, 0.0),
        (TemperatureUnits.CELSIUS, TemperatureUnits.FAHRENHEIT): (1.8, 32.0),
        (TemperatureUnits.CELSIUS, TemperatureUnits.KELVIN): (1.0, 273.15),
        (TemperatureUnits.FAHRENHEIT, TemperatureUnits.FAHRENHEIT): (1.0, 0.0),
        (TemperatureUnits.FAHRENHEIT, TemperatureUnits.CELSIUS): (
            0.5555555556,
            -17.7777777778,
        ),
        (TemperatureUnits.FAHRENHEIT, TemperatureUnits.KELVIN): (
            0.5555555556,
            255.3722222222,
        ),
        (TemperatureUnits.KELVIN, TemperatureUnits.KELVIN): (1.0, 0.0),
        (TemperatureUnits.KELVIN, TemperatureUnits.CELSIUS): (1.0, -273.15),
        (TemperatureUnits.KELVIN, TemperatureUnits.FAHRENHEIT): (1.8, -459.67),
    }

    conversion_key = (from_unit, to_unit)
    conversion_factors = conversion_factors.get(conversion_key)

    if conversion_factors is None:
        raise ValueError(
            f"Conversion from {from_unit.value} to {to_unit.value} is not supported."
        )

    return conversion_factors


def convert_temperature_values(
    values: Tuple[Union[float, None]],
    from_unit: TemperatureUnits,
    to_unit: TemperatureUnits,
) -> Tuple[Union[float, None]]:
    """
    Converts temperature values from one unit to another.

    :param values: The temperature values to be converted.
    :type values: Tuple[Union[float, None]]
    :param from_unit: The unit of the input temperature values.
    :type from_unit: TemperatureUnits
    :param to_unit: The desired unit for the converted temperature values.
    :type to_unit: TemperatureUnits
    :return: The converted temperature values.
    :rtype: Tuple[Union[float, None]]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion = get_temperature_conversion(from_unit, to_unit)
    converted_values = [
        (value * conversion[0]) + conversion[1] if value is not None else None
        for value in values
    ]
    return tuple(converted_values)


class MassFlowUnits(Enum):
    """
    Enumeration of mass flow units.
    """

    UL_MIN = 0
    UL_HR = 1
    ML_MIN = 2
    ML_HR = 3


def get_mass_flow_conversion(
    from_unit: MassFlowUnits, to_unit: MassFlowUnits
) -> Union[float, None]:
    """
    Retrieves the conversion factor between two mass flow units.

    :param from_unit: The source mass flow unit.
    :type from_unit: MassFlowUnits
    :param to_unit: The target mass flow unit.
    :type to_unit: MassFlowUnits
    :return: The conversion factor from the source unit to the target unit.
    :rtype: Union[float, None]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion_factors = {
        (MassFlowUnits.ML_MIN, MassFlowUnits.UL_MIN): 1000.0,
        (MassFlowUnits.ML_MIN, MassFlowUnits.UL_HR): 60000.0,
        (MassFlowUnits.ML_MIN, MassFlowUnits.ML_MIN): 1.0,
        (MassFlowUnits.ML_MIN, MassFlowUnits.ML_HR): 60.0,
    }

    conversion_key = (from_unit, to_unit)
    conversion_factor = conversion_factors.get(conversion_key)

    if conversion_factor is None:
        raise ValueError(
            f"Conversion from {from_unit.value} to {to_unit.value} is not supported."
        )

    return conversion_factor


def convert_mass_flow_values(
    values: Tuple[Union[float, None]], from_unit: MassFlowUnits, to_unit: MassFlowUnits
) -> Tuple[Union[float, None]]:
    """
    Converts mass flow values from one unit to another.

    :param values: The mass flow values to be converted.
    :type values: Tuple[Union[float, None]]
    :param from_unit: The unit of the input mass flow values.
    :type from_unit: MassFlowUnits
    :param to_unit: The desired unit for the converted mass flow values.
    :type to_unit: MassFlowUnits
    :return: The converted mass flow values.
    :rtype: Tuple[Union[float, None]]
    :raises ValueError: If the conversion from the input unit to the desired unit is not supported.
    """
    conversion_factor = get_mass_flow_conversion(from_unit, to_unit)

    converted_values = [
        value * conversion_factor if value is not None else None for value in values
    ]

    return tuple(converted_values)


class OpticalDensityUnits(Enum):
    """
    Enumeration of optical density units.
    """

    OPTICAL_DENSITY = 0
    TRANSMITTED = (1,)
    NINETY = (2,)
