# pylint: disable=line-too-long
"""
The `aqueduct.devices.factory` module provides a simple factory function for creating instances of different devices
that are used in Aqueduct.

Functions:
- create_device(kind: str, socket, socket_lock, **kwargs) -> typing.Union[aqueduct.devices.base.obj.Device, None]:
    This function creates a new instance of the device specified by `kind`. The available device kinds are:
    - "balance": an instance of `aqueduct.devices.balance.Balance`.
    - "optical_density_probe": an instance of `aqueduct.devices.optical_density.OpticalDensityProbe`.
    - "peristaltic_pump": an instance of `aqueduct.devices.pump.peristaltic.PeristalticPump`.
    - "ph_probe": an instance of `aqueduct.devices.ph_probe.PhProbe`.
    - "pinch_valve": an instance of `aqueduct.devices.valve.pinch.PinchValve`.
    - "pressure_transducer": an instance of `aqueduct.devices.pressure.transducer.PressureTransducer`.
    - "syringe_pump": an instance of `aqueduct.devices.pump.syringe.SyringePump`.
    - "test_device": an instance of `aqueduct.devices.test_device.TestDevice`.

    Parameters:
    - kind (str): The kind of device to create.
    - socket: The socket to use for communication with the device.
    - socket_lock: A lock to use to prevent concurrent access to the socket.
    - **kwargs: Additional keyword arguments to pass to the device constructor.

    Returns:
    - An instance of the specified device, or None if `kind` is not recognized.
"""
# pylint: enable=line-too-long
import typing
from enum import Enum

import aqueduct.devices.balance
import aqueduct.devices.mass_flow
import aqueduct.devices.optical_density
import aqueduct.devices.ph
import aqueduct.devices.pressure.transducer
import aqueduct.devices.pump.peristaltic
import aqueduct.devices.temperature
import aqueduct.devices.test_device
import aqueduct.devices.valve.pinch
import aqueduct.devices.valve.solenoid


class DeviceTypes(Enum):
    PERISTALTIC_PUMP = "peristaltic_pump"
    SYRINGE_PUMP = "syringe_pump"
    DIAPHRAGM_PUMP = "diaphragm_pump"
    PISTON_PUMP = "piston_pump"
    SOLENOID_VALVE = "solenoid_valve"
    ROTARY_VALVE = "rotary_valve"
    PINCH_VALVE = "pinch_valve"
    TEMPERATURE_PROBE = "temperature_probe"
    PH_PROBE = "ph_probe"
    OPTICAL_DENSITY = "optical_density"
    MIXER = "mixer"
    CARTESIAN_ROBOT = "cartesian_robot"
    SCADA_ROBOT = "scada_robot"
    COLLABORATIVE_ROBOT = "collaborative_robot"
    LED = "led"
    DISSOLVED_OXYGEN = "dissolved_oxygen"
    MASS_FLOW_METER = "mass_flow_meter"
    MASS_FLOW_CONTROLLER = "mass_flow_controller"
    PRESSURE_CONTROLLER = "pressure_controller"
    PRESSURE_TRANSDUCER = "pressure_transducer"
    BALANCE = "balance"
    LOAD_CELL = "load_cell"
    STEPPER_MOTOR = "stepper_motor"
    SERVO_MOTOR = "servo_motor"
    BRUSHLESS_MOTOR = "brushless_motor"
    SOLENOID = "solenoid"
    BUTTON = "button"
    SWITCH = "switch"
    TEST_DEVICE = "test_device"
    UNKNOWN = "unknown"


def create_device(
    kind: str, socket, socket_lock, **kwargs
) -> typing.Union[aqueduct.devices.base.obj.Device, None]:
    """Create an instance of a device object of a specified type.

    :param kind: (str) Name of device type to create.
    :param socket: Socket connection to device.
    :param socket_lock: Lock for the socket connection.
    :param kwargs: Any additional arguments required by the device constructor.

    :return: Instance of a device object of the specified type.
    :rtype: Device object
    """
    device = None

    if kind == DeviceTypes.BALANCE.value:
        device = aqueduct.devices.balance.Balance(socket, socket_lock, **kwargs)
    elif kind == DeviceTypes.MASS_FLOW_METER.value:
        device = aqueduct.devices.mass_flow.MassFlowMeter(socket, socket_lock, **kwargs)
    elif kind == DeviceTypes.OPTICAL_DENSITY.value:
        device = aqueduct.devices.optical_density.OpticalDensityProbe(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.PERISTALTIC_PUMP.value:
        device = aqueduct.devices.pump.peristaltic.PeristalticPump(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.PH_PROBE.value:
        device = aqueduct.devices.ph.PhProbe(socket, socket_lock, **kwargs)
    elif kind == DeviceTypes.PINCH_VALVE.value:
        device = aqueduct.devices.valve.pinch.PinchValve(socket, socket_lock, **kwargs)
    elif kind == DeviceTypes.PRESSURE_TRANSDUCER.value:
        device = aqueduct.devices.pressure.transducer.PressureTransducer(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.SOLENOID_VALVE.value:
        device = aqueduct.devices.valve.solenoid.SolenoidValve(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.SYRINGE_PUMP.value:
        device = aqueduct.devices.pump.syringe.SyringePump(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.TEMPERATURE_PROBE.value:
        device = aqueduct.devices.temperature.TemperatureProbe(
            socket, socket_lock, **kwargs
        )
    elif kind == DeviceTypes.TEST_DEVICE.value:
        device = aqueduct.devices.test_device.TestDevice(socket, socket_lock, **kwargs)
    return device
