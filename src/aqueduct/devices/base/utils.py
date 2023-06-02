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

import aqueduct.devices.balance
import aqueduct.devices.optical_density
import aqueduct.devices.ph
import aqueduct.devices.pressure.transducer
import aqueduct.devices.pump.peristaltic
import aqueduct.devices.test_device
import aqueduct.devices.valve.pinch


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

    if kind == "balance":
        device = aqueduct.devices.balance.Balance(socket, socket_lock, **kwargs)
    elif kind == "optical_density":
        device = aqueduct.devices.optical_density.OpticalDensityProbe(
            socket, socket_lock, **kwargs
        )
    elif kind == "peristaltic_pump":
        device = aqueduct.devices.pump.peristaltic.PeristalticPump(
            socket, socket_lock, **kwargs
        )
    elif kind == "ph_probe":
        device = aqueduct.devices.ph.PhProbe(socket, socket_lock, **kwargs)
    elif kind == "pinch_valve":
        device = aqueduct.devices.valve.pinch.PinchValve(socket, socket_lock, **kwargs)
    elif kind == "pressure_transducer":
        device = aqueduct.devices.pressure.transducer.PressureTransducer(
            socket, socket_lock, **kwargs
        )
    elif kind == "syringe_pump":
        device = aqueduct.devices.pump.syringe.SyringePump(
            socket, socket_lock, **kwargs
        )
    elif kind == "test_device":
        device = aqueduct.devices.test_device.TestDevice(socket, socket_lock, **kwargs)
    return device
