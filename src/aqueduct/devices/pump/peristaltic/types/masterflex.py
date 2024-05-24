class MixedSignal:
    """
    Configuration data for a MasterFlex peristaltic pump.

    :param masterflex_sn: Serial number of the MasterFlex pump.
    :type masterflex_sn: str
    :param rx_adc_ml_min_value_high: The high value for ADC reading corresponding to max flow rate in ml/min.
    :type rx_adc_ml_min_value_high: float
    :param rx_adc_ml_min_value_low: The low value for ADC reading corresponding to min flow rate in ml/min.
    :type rx_adc_ml_min_value_low: float
    :param rx_adc_read_value_high: The high value of ADC reading.
    :type rx_adc_read_value_high: float
    :param rx_adc_read_value_low: The low value of ADC reading.
    :type rx_adc_read_value_low: float
    :param tx_adc_ml_min_value_high: The high command value corresponding to max flow rate in ml/min.
    :type tx_adc_ml_min_value_high: float
    :param tx_adc_ml_min_value_low: The low command value corresponding to min flow rate in ml/min.
    :type tx_adc_ml_min_value_low: float
    :param tx_adc_write_value_high: The high value for ADC command.
    :type tx_adc_write_value_high: float
    :param tx_adc_write_value_low: The low value for ADC command.
    :type tx_adc_write_value_low: float
    """

    def __init__(self, masterflex_sn: str, rx_adc_ml_min_value_high: float, rx_adc_ml_min_value_low: float,
                 rx_adc_read_value_high: float, rx_adc_read_value_low: float,
                 tx_adc_ml_min_value_high: float, tx_adc_ml_min_value_low: float,
                 tx_adc_write_value_high: float, tx_adc_write_value_low: float):
        self.masterflex_sn = masterflex_sn
        self.rx_adc_ml_min_value_high = rx_adc_ml_min_value_high
        self.rx_adc_ml_min_value_low = rx_adc_ml_min_value_low
        self.rx_adc_read_value_high = rx_adc_read_value_high
        self.rx_adc_read_value_low = rx_adc_read_value_low
        self.tx_adc_ml_min_value_high = tx_adc_ml_min_value_high
        self.tx_adc_ml_min_value_low = tx_adc_ml_min_value_low
        self.tx_adc_write_value_high = tx_adc_write_value_high
        self.tx_adc_write_value_low = tx_adc_write_value_low

    def to_dict(self) -> dict:
        """
        Convert the StepperMotorConfig instance to a dictionary, excluding None values.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_config(cls, **data) -> "MixedSignal":
        """
        Create a `MasterFlexConfig` instance from a configuration dictionary.

        :param data: Configuration data.
        :type data: dict
        :return: The created `MasterFlexConfig` instance.
        :rtype: MasterFlexConfig
        """
        return cls(**data)

    def update_from_command(self, command: dict) -> None:
        """
        Update the configuration from a command dictionary.

        Each field is checked for presence in the command dictionary before updating.
        """
        for attr in ['masterflex_sn', 'rx_adc_ml_min_value_high', 'rx_adc_ml_min_value_low',
                     'rx_adc_read_value_high', 'rx_adc_read_value_low',
                     'tx_adc_ml_min_value_high', 'tx_adc_ml_min_value_low',
                     'tx_adc_write_value_high', 'tx_adc_write_value_low']:
            if attr in command:
                setattr(self, attr, command[attr])
