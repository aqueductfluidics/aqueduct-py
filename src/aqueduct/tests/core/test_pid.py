import pytest

from aqueduct.core.pid import Pid


class TestPid:

    def test_default_values(self):
        pid = Pid(setpoint=100.0)
        assert not pid.enabled
        assert pid.update_interval_ms == 1000
        assert pid.setpoint == 100.0
        assert pid.bias == 0.0
        assert pid.kp == 0.0
        assert pid.ki == 0.0
        assert pid.kd == 0.0
        assert pid.p_limit is None
        assert pid.i_limit is None
        assert pid.d_limit is None
        assert pid.integral_term == 0.0
        assert pid.delta_limits is None
        assert pid.control_bounds == (None, None)
        assert pid.output_limits == (None, None)
        assert pid.dead_zone is None

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
        assert pid.bias == 10.0
        assert pid.kp == 1.0
        assert pid.ki == 0.5
        assert pid.kd == 0.2
        assert pid.p_limit == 10.0
        assert pid.i_limit == 5.0
        assert pid.d_limit == 2.0
        assert pid.integral_term == 2.5
        assert pid.delta_limits == (5.0, 2.0)
        assert pid.control_bounds == (0.0, 100.0)
        assert pid.output_limits == (-10.0, 10.0)
        assert pid.dead_zone == (0.1, 0.1)

    def test_invalid_values(self):
        pid = Pid(setpoint=100.0, invalid_attribute=5.0)
        assert hasattr(pid, "invalid_attribute") is False
