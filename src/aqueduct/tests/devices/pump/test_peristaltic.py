import pytest
from unittest.mock import MagicMock
from aqueduct.devices.pump.peristaltic import PeristalticPump, Config
from aqueduct.devices.pump.peristaltic.types.aqueduct import StepperMotorConfig
from aqueduct.devices.pump.peristaltic.types.masterflex import MixedSignal
from aqueduct.devices.base.obj import DeviceKeys, DeviceBaseKeys, Interface, Actions
# pylint: disable=unused-import
from aqueduct.tests.devices.test_utils import mock_lock, mock_socket


@pytest.fixture
def pump(mock_socket, mock_lock):
    kwargs = {
        DeviceKeys.Base.value: {
            DeviceBaseKeys.DeviceId.value: 1,
            DeviceBaseKeys.UserId.value: "user_id",
            DeviceBaseKeys.Type.value: "peristaltic_pump",
            DeviceBaseKeys.Name.value: "name",
            DeviceBaseKeys.Interface.value: Interface.Sim,
        },
        DeviceKeys.Live.value: [
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0},
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0},
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0},
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0},
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0},
            {"mt": 0.0, "md": 0.0, "mm": 0.0, "s": 0, "m": 0}
        ],
        DeviceKeys.Stat.value: [
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0},
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0},
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0},
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0},
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0},
            {"tubing_length_mm": 0.0, "tubing_id_mm": 0.0, "max_ml_min": 0.0}
        ],
        DeviceKeys.Config.value: {
            "type": Config.StepperMotor.value,
            "config": {
                "protocol": 0,
                "data": [
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0},
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0},
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0},
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0},
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0},
                    {"rev_per_ml": 24.0, "steps_per_rev": 200.0}
                ]
            }
        }
    }
    pump = PeristalticPump(mock_socket, mock_lock, **kwargs)
    pump.get_config_and_cast = MagicMock(return_value={
        "type": Config.StepperMotor.value,
        "config": {
            "data": [
                {
                    "rev_per_ml": 1.0,
                    "steps_per_rev": 200.0
                }
            ]
        }
    })
    pump.send_command = MagicMock()
    return pump


class TestPeristalticPump:
    def test_set_config_stepper_motor(self, pump):
        config = [StepperMotorConfig(rev_per_ml=2.0, steps_per_rev=None)]

        pump.set_config(config)

        expected_payload = {
            "action": Actions.SetConfig,
            "command": {
                "config":
                [
                       {
                           "rev_per_ml": 2.0,
                           "steps_per_rev": 200.0
                       }
                ],
                "base": {},
                "stat": []
            }
        }

        # Check if the payload sent matches the expected payload
        pump.send_command.assert_called_once()
        # Get the CommandPayload object
        called_args = pump.send_command.call_args[0][0]
        assert called_args.command["config"][0] == expected_payload["command"]["config"][0]

    def test_set_config_mixed_signal(self, pump):
        pump.get_config_and_cast = MagicMock(return_value={
            "type": Config.MixedSignal.value,
            "config": {
                "data": [
                    {
                        "masterflex_sn": "12345",
                        "rx_adc_ml_min_value_high": 10.0,
                        "rx_adc_ml_min_value_low": 1.0,
                        "rx_adc_read_value_high": 1023.0,
                        "rx_adc_read_value_low": 0.0,
                        "tx_adc_ml_min_value_high": 10.0,
                        "tx_adc_ml_min_value_low": 1.0,
                        "tx_adc_write_value_high": 1023.0,
                        "tx_adc_write_value_low": 0.0
                    }
                ]
            }
        })

        config = [MixedSignal(
            masterflex_sn="67890",
            rx_adc_ml_min_value_high=20.0,
            rx_adc_ml_min_value_low=2.0,
            rx_adc_read_value_high=2047.0,
            rx_adc_read_value_low=0.5,
            tx_adc_ml_min_value_high=20.0,
            tx_adc_ml_min_value_low=2.0,
            tx_adc_write_value_high=2047.0,
            tx_adc_write_value_low=0.5
        )]

        pump.set_config(config)

        expected_payload = {
            "action": Actions.SetConfig,
            "command": {
                "config":
                [
                    {
                        "masterflex_sn": "67890",
                        "rx_adc_ml_min_value_high": 20.0,
                        "rx_adc_ml_min_value_low": 2.0,
                        "rx_adc_read_value_high": 2047.0,
                        "rx_adc_read_value_low": 0.5,
                        "tx_adc_ml_min_value_high": 20.0,
                        "tx_adc_ml_min_value_low": 2.0,
                        "tx_adc_write_value_high": 2047.0,
                        "tx_adc_write_value_low": 0.5
                    }
                ],
                "base": {},
                "stat": []
            }
        }

        # Check if the payload sent matches the expected payload
        pump.send_command.assert_called_once()
        # Get the CommandPayload object
        called_args = pump.send_command.call_args[0][0]
        assert called_args.command["config"][0] == expected_payload["command"]["config"][0]

    def test_set_config_no_modifications(self, pump):
        config = []

        pump.set_config(config)

        expected_payload = {
            "action": Actions.SetConfig,
            "command": {
                "config":
                [
                    {},
                ],
                "base": {},
                "stat": []
            }
        }

        # Check if the payload sent matches the expected payload
        pump.send_command.assert_called_once()
        # Get the CommandPayload object
        called_args = pump.send_command.call_args[0][0]
        assert called_args.command["config"] == expected_payload["command"]["config"]
