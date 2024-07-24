from enum import Enum

# pylint: disable=invalid-name
class StepperMotorConfigKeys(Enum):
    """
    Enum representing the keys of StepperMotorConfig.
    """

    RevPerMl = "rev_per_ml"
    StepsPerRev = "steps_per_rev"


class StepperMotorConfig:
    """
    Configuration data for a stepper motor pump.

    :param rev_per_ml: Number of revolutions per milliliter.
    :type rev_per_ml: float
    :param steps_per_rev: Number of steps per revolution.
    :type steps_per_rev: float
    """

    def __init__(self, rev_per_ml: float, steps_per_rev: float):
        self.rev_per_ml = rev_per_ml
        self.steps_per_rev = steps_per_rev

    def to_dict(self) -> dict:
        """
        Convert the StepperMotorConfig instance to a dictionary, excluding None values.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_config(cls, **data) -> "StepperMotorConfig":
        """
        Create a `StepperMotorConfig` instance from a configuration dictionary.

        :param data: Configuration data.
        :type data: dict
        :return: The created `StepperMotorConfig` instance.
        :rtype: StepperMotorConfig
        """
        return StepperMotorConfig(**data)

    def update_from_command(self, command: dict) -> None:
        """
        Update the configuration from a command dictionary.

        :param command: Command dictionary.
        :type command: dict
        """
        if "rev_per_ml" in command:
            self.rev_per_ml = command["rev_per_ml"]

        if "steps_per_rev" in command:
            self.steps_per_rev = command["steps_per_rev"]
