import enum

# pylint: disable=invalid-name
class Config(enum.Enum):
    """
    Enum representing the configuration types.
    """

    StepperMotor = "StepperMotor"
    MixedSignal = "MixedSignal"
