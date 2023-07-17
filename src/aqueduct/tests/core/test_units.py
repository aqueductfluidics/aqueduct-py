import math

import pytest
from aqueduct.core.units import convert_pressure_values
from aqueduct.core.units import convert_temperature_values
from aqueduct.core.units import PressureUnits
from aqueduct.core.units import TemperatureUnits


class TestTemperatureConversionUtils:
    def test_temperature_conversion(self):
        abs_tol = 1.0e-8

        # Test Celsius to Fahrenheit
        assert math.isclose(
            convert_temperature_values(
                (0,), TemperatureUnits.CELSIUS, TemperatureUnits.FAHRENHEIT
            )[0],
            32.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (25,), TemperatureUnits.CELSIUS, TemperatureUnits.FAHRENHEIT
            )[0],
            77.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (-10,), TemperatureUnits.CELSIUS, TemperatureUnits.FAHRENHEIT
            )[0],
            14.0,
            abs_tol=abs_tol,
        )

        # Test Fahrenheit to Celsius
        assert math.isclose(
            convert_temperature_values(
                (32,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.CELSIUS
            )[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (77,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.CELSIUS
            )[0],
            25.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (14,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.CELSIUS
            )[0],
            -10.0,
            abs_tol=abs_tol,
        )

        # Test Celsius to Kelvin
        assert math.isclose(
            convert_temperature_values(
                (0,), TemperatureUnits.CELSIUS, TemperatureUnits.KELVIN
            )[0],
            273.15,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (25,), TemperatureUnits.CELSIUS, TemperatureUnits.KELVIN
            )[0],
            298.15,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (-10,), TemperatureUnits.CELSIUS, TemperatureUnits.KELVIN
            )[0],
            263.15,
            abs_tol=abs_tol,
        )

        # Test Kelvin to Celsius
        assert math.isclose(
            convert_temperature_values(
                (273.15,), TemperatureUnits.KELVIN, TemperatureUnits.CELSIUS
            )[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (298.15,), TemperatureUnits.KELVIN, TemperatureUnits.CELSIUS
            )[0],
            25.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (263.15,), TemperatureUnits.KELVIN, TemperatureUnits.CELSIUS
            )[0],
            -10.0,
            abs_tol=abs_tol,
        )

        # Test Fahrenheit to Kelvin
        assert math.isclose(
            convert_temperature_values(
                (32,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.KELVIN
            )[0],
            273.15,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (77,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.KELVIN
            )[0],
            298.15,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (14,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.KELVIN
            )[0],
            263.15,
            abs_tol=abs_tol,
        )

        # Test Kelvin to Fahrenheit
        assert math.isclose(
            convert_temperature_values(
                (273.15,), TemperatureUnits.KELVIN, TemperatureUnits.FAHRENHEIT
            )[0],
            32.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (298.15,), TemperatureUnits.KELVIN, TemperatureUnits.FAHRENHEIT
            )[0],
            77.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (263.15,), TemperatureUnits.KELVIN, TemperatureUnits.FAHRENHEIT
            )[0],
            14.0,
            abs_tol=abs_tol,
        )

        # Test same units
        assert math.isclose(
            convert_temperature_values(
                (0,), TemperatureUnits.CELSIUS, TemperatureUnits.CELSIUS
            )[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (32,), TemperatureUnits.FAHRENHEIT, TemperatureUnits.FAHRENHEIT
            )[0],
            32.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_temperature_values(
                (273.15,), TemperatureUnits.KELVIN, TemperatureUnits.KELVIN
            )[0],
            273.15,
            abs_tol=abs_tol,
        )


class TestPressureConversionUtils:
    def test_pressure_conversion(self):
        abs_tol = 1.0e-8

        # Test Torr to Psi
        assert math.isclose(
            convert_pressure_values((0,), PressureUnits.TORR, PressureUnits.PSI)[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((100,), PressureUnits.TORR, PressureUnits.PSI)[0],
            1.93367758,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((500,), PressureUnits.TORR, PressureUnits.PSI)[0],
            9.6683879,
            abs_tol=abs_tol,
        )

        # Test Torr to AtmosphereStd
        assert math.isclose(
            convert_pressure_values(
                (0,), PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD
            )[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values(
                (1000,), PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD
            )[0],
            1.31578947,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values(
                (5000,), PressureUnits.TORR, PressureUnits.ATMOSPHERE_STD
            )[0],
            6.57894735,
            abs_tol=abs_tol,
        )

        # Test Torr to Pascal
        assert math.isclose(
            convert_pressure_values((0,), PressureUnits.TORR, PressureUnits.PASCAL)[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((500,), PressureUnits.TORR, PressureUnits.PASCAL)[
                0
            ],
            66661.184,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((1000,), PressureUnits.TORR, PressureUnits.PASCAL)[
                0
            ],
            133322.368,
            abs_tol=abs_tol,
        )

        # Test Torr to Bar
        assert math.isclose(
            convert_pressure_values((0,), PressureUnits.TORR, PressureUnits.BAR)[0],
            0.0,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((500,), PressureUnits.TORR, PressureUnits.BAR)[0],
            0.66661184,
            abs_tol=abs_tol,
        )
        assert math.isclose(
            convert_pressure_values((1000,), PressureUnits.TORR, PressureUnits.BAR)[0],
            1.33322368,
            abs_tol=abs_tol,
        )
