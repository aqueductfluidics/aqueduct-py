# pylint: disable=protected-access, missing-function-docstring, missing-class-docstring, redefined-outer-name, unused-variable, unused-argument
from unittest.mock import MagicMock

import pytest
from aqueduct.core.pid import Pid
from aqueduct.core.pid import PidController
from aqueduct.core.pid import Schedule
from aqueduct.core.pid import ScheduleParameters


class TestPid:
    def test_default_values(self):
        pid = Pid(setpoint=100.0)
        assert not pid.enabled
        assert pid.update_interval_ms == 1000
        assert pid.setpoint == 100.0
        assert pid.integral_term == 0.0
        assert pid.output_limits == (None, None)

    def test_custom_values(self):
        pid = Pid(
            setpoint=50.0,
            update_interval_ms=500,
            bias=10.0,
            kp=1.0,
            ki=0.5,
            kd=0.2,
            p_limit=10.0,
            i_limit=5.0,
            d_limit=2.0,
            integral_term=2.5,
            delta_limits=(5.0, 2.0),
            control_bounds=(0.0, 100.0),
            output_limits=(-10.0, 10.0),
            dead_zone=(0.1, 0.1),
        )
        assert pid.setpoint == 50.0
        assert pid.update_interval_ms == 500
        assert pid.integral_term == 2.5
        assert pid.output_limits == (-10.0, 10.0)

    def test_invalid_values(self):
        pid = Pid(setpoint=100.0, invalid_attribute=5.0)
        assert hasattr(pid, "invalid_attribute") is False


@pytest.fixture
def mock_pid_controller():
    pid_params = Pid(100)
    return PidController(
        name="MockController",
        process_value=None,
        control_value=None,
        pid_params=pid_params,
    )


@pytest.fixture
def mock_pid():
    return Pid(100)


@pytest.fixture
def mock_aqueduct():
    class MockAqueduct:
        def send_and_wait_for_rx(self, message, event, attempts):
            # Simulate sending a message and receiving a response
            return True, '{"controllers": {"1": {"pid": {"enabled": true}}}}'

        def create_pid_controller(self, controller: PidController):
            # Simulate sending a message and receiving a response
            controller._aq = self

    return MockAqueduct()


def test_change_setpoint_serialization(mock_pid_controller):
    mock_pid_controller._update = MagicMock()

    mock_pid_controller.change_setpoint(setpoint=30.0, clear_integral=True)

    expected_serialized_data = {"setpoint": 30.0, "integral_term": 0.0}

    mock_pid_controller._update.assert_called_once_with(
        mock_pid_controller.pid._serialize_selected(
            list(expected_serialized_data.keys())
        )
    )


def test_enable_pid_controller_serialization(mock_aqueduct):
    pid_controller = PidController(
        name="test", process_value=None, control_value=None, pid_params=Pid(100)
    )
    pid_controller._assign(mock_aqueduct)

    pid_controller.enable()

    serialized = pid_controller._serialize_update(
        pid_controller.pid._serialize_selected(["enabled"])
    )

    assert serialized == {"id": None, "pid": {"enabled": True}}


def test_disable_pid_controller_serialization(mock_aqueduct):
    pid_controller = PidController(
        name="test", process_value=None, control_value=None, pid_params=Pid(100)
    )
    pid_controller._assign(mock_aqueduct)

    pid_controller.disable()

    serialized = pid_controller._serialize_update(
        pid_controller.pid._serialize_selected(["enabled"])
    )

    assert serialized == {"id": None, "pid": {"enabled": False}}


def test_clear_integral_pid_controller_serialization(mock_aqueduct):
    pid_controller = PidController(
        name="test", process_value=None, control_value=None, pid_params=Pid(100)
    )
    pid_controller._assign(mock_aqueduct)

    pid_controller.clear_integral()

    serialized = pid_controller._serialize_update(
        pid_controller.pid._serialize_selected(["integral_term"])
    )

    assert serialized == {"id": None, "pid": {"integral_term": 0.0}}


def test_change_parameters_serialization(mock_pid_controller, mock_pid, mock_aqueduct):
    schedule = Schedule(controller=ScheduleParameters())

    mock_aqueduct.create_pid_controller(mock_pid_controller)

    mock_pid_controller.pid.add_schedule(schedule)

    mock_pid_controller.pid.schedule[0].change_parameters(
        kp=1.0, ki=0.5, kd=0.2, bias=0.1
    )

    expected_update_schedule = [{"bias": 0.1, "kp": 1.0, "ki": 0.5, "kd": 0.2}]

    expected_update_dict = {"pid": {"controllers": expected_update_schedule}}
