import pytest
from aqueduct.devices.pump.syringe import Status


class TestSyringePump:
    def test_int_to_status(self) -> None:
        s = Status.Infusing.value
        assert s == 1
        assert Status(s) == Status.Infusing

    def test_reverse(self) -> None:
        s = Status.Infusing
        s = s.reverse()
        assert s == Status.Withdrawing
        s = s.reverse()
        assert s == Status.Infusing
        s = Status.Stopped
        s = s.reverse()
        assert s == Status.Stopped
        s = Status.Paused
        s = s.reverse()
        assert s == Status.Paused
