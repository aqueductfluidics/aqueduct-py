import pytest
from aqueduct.core.utils import split_packets


class TestCoreUtils:
    def test_split_packets(self):
        message = b'["set_recipe_input","ack"]["get_recipe_input_value","{\\"value\\":\\"[{\\\\\\"value\\\\\\":\\\\\\"50\\\\\\",\\\\\\"name\\\\\\":\\\\\\"log_file_name\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"polysach_mass\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"init_cont_g_L\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"init_product_vol_ml\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"initial_transfer_volume\\\\\\"}]\\"}"]'
        expected = (
            b'["set_recipe_input","ack"]',
            b'["get_recipe_input_value","{\\"value\\":\\"[{\\\\\\"value\\\\\\":\\\\\\"50\\\\\\",\\\\\\"name\\\\\\":\\\\\\"log_file_name\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"polysach_mass\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"init_cont_g_L\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"init_product_vol_ml\\\\\\"},{\\\\\\"value\\\\\\":\\\\\\"050\\\\\\",\\\\\\"name\\\\\\":\\\\\\"initial_transfer_volume\\\\\\"}]\\"}"]',
        )

        result = split_packets(message)
        assert result == expected

    def test_single_packet(self):
        message = b'["set_recipe_input","ack"]'
        expected = (b'["set_recipe_input","ack"]',)
        result = split_packets(message)
        assert result == expected
