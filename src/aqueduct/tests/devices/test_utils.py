from unittest.mock import Mock

import aqueduct.devices.balance
import aqueduct.devices.optical_density
import aqueduct.devices.ph
import aqueduct.devices.pressure.transducer
import aqueduct.devices.pump.peristaltic
import aqueduct.devices.temperature
import aqueduct.devices.test_device
import aqueduct.devices.valve.pinch
import aqueduct.devices.valve.solenoid
import pytest
from aqueduct.devices.base.obj import Device
from aqueduct.devices.base.obj import DeviceBaseKeys
from aqueduct.devices.base.obj import DeviceKeys
from aqueduct.devices.base.obj import Interface
from aqueduct.devices.base.utils import create_device
from aqueduct.devices.base.utils import DeviceTypes


@pytest.fixture
def mock_socket():
    return Mock()


@pytest.fixture
def mock_lock():
    return Mock()


def test_device_init(mock_socket, mock_lock):
    kwargs = {
        DeviceKeys.Base.value: {
            DeviceBaseKeys.DeviceId.value: 1,
            DeviceBaseKeys.UserId.value: "user_id",
            DeviceBaseKeys.Type.value: "type",
            DeviceBaseKeys.Name.value: "name",
            DeviceBaseKeys.Interface.value: Interface.Sim,
        },
        DeviceKeys.Live.value: [1, 2, 3],  # Example live data
    }

    device = Device(mock_socket, mock_lock, **kwargs)

    assert device._socket == mock_socket
    assert device._socket_lock == mock_lock
    assert device._device_id == 1
    assert device._user_id == "user_id"
    assert device._type == "type"
    assert device._name == "name"
    assert device._interface == Interface.Sim
    assert device._len == 3  # Length of live data
    assert device._command_delay == 0.0  # Assert default value for _command_delay
    # Assert default value for _has_sim_values
    assert device._has_sim_values == False
