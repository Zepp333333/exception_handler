from unittest import mock

from exception_handler_plus.read_env import read_env_as_int


@mock.patch('os.getenv', return_value=None)
def test_read_env_no_env(*_mocks):
    assert read_env_as_int('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS') is None


@mock.patch('os.getenv', return_value='wrong_env_var_value')
def test_read_env_non_digit_env_var(*_mocks):
    assert read_env_as_int('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS') is None


@mock.patch('os.getenv', return_value='5')
def test_read_env_digit_env_var(*_mocks):
    assert read_env_as_int('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS') == 5
