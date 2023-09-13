# pylint: disable=unused-import, singleton-comparison, protected-access, missing-function-docstring, missing-class-docstring, redefined-outer-name, unused-variable, unused-argument
import pytest
from aqueduct.core.aq import InitParams


def test_init_params_initialization():
    """Test the __init__ method"""
    params = InitParams("JohnDoe", "127.0.0.1", 8080, True, False)
    assert params.user_id == "JohnDoe"
    assert params.ip_address == "127.0.0.1"
    assert params.port == 8080
    assert params.init == True
    assert params.register_process == False


def test_init_params_parse_all_arguments(monkeypatch):
    """Test parsing with all arguments"""
    testargs = [
        "prog",
        "-u",
        "1",
        "-a",
        "127.0.0.1",
        "-p",
        "8080",
        "-i",
        "1",
        "-r",
        "0",
    ]
    monkeypatch.setattr("sys.argv", testargs)

    params = InitParams.parse()

    assert params.user_id == "1"
    assert params.ip_address == "127.0.0.1"
    assert params.port == 8080
    assert params.init == True
    assert params.register_process == False


def test_init_params_parse_missing_optional_args(monkeypatch):
    """Test parsing with missing optional arguments (defaults should be used)"""
    testargs = ["prog", "-u", "1", "-a", "127.0.0.1", "-p", "8080", "-i", "1"]
    monkeypatch.setattr("sys.argv", testargs)

    params = InitParams.parse()

    assert params.register_process == True  # This should use the default value


def test_init_params_parse_no_args(monkeypatch):
    """Test parsing with no arguments (all should be None or default)"""
    testargs = ["prog"]
    monkeypatch.setattr("sys.argv", testargs)

    params = InitParams.parse()

    assert params.user_id == None
    assert params.ip_address == None
    assert params.port == None
    assert params.init == False  # because bool(None) is False
    assert params.register_process == True  # This should use the default value
