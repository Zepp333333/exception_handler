import logging
from collections import defaultdict
from typing import Callable, Dict, Type

import pytest

from exception_handler import HandlerFuncType, exception_handler, get_handler_for_exception, MaxRepeatedExceptionsError, \
    is_exceeded_max_repeated_exceptions

logger = logging.getLogger(__name__)

HANDLED_ATTRIBUTE_ERROR = 'handled_attribute_error'
HANDLED_LOGGING = 'handled_logging'
DEFAULT_RETURN = 'default_return'


class RepeatedError(Exception):
    pass


class RetryThisError(Exception):
    pass


class LogThisError(Exception):
    pass


def attribute_error_handler(_func: Callable):
    return HANDLED_ATTRIBUTE_ERROR


def logging_handler(func):
    logger.warning(HANDLED_LOGGING)
    return func()


def retry_handler(func: Callable, *args, **kwargs):
    return func(*args, **kwargs)


test_handlers: Dict[Type[Exception], HandlerFuncType] = {
    AttributeError: attribute_error_handler,
    RetryThisError: retry_handler,
    RepeatedError: retry_handler,
    LogThisError: logging_handler
}


def test_get_handler_for_exception_positive():
    assert get_handler_for_exception(test_handlers, AttributeError()) == attribute_error_handler


def test_get_handler_for_exception_negative():
    assert get_handler_for_exception(test_handlers, RuntimeError()) is None


def test_exception_handler_no_exception():
    @exception_handler(handlers=test_handlers)
    def func():
        return 512

    assert func() == 512


def test_exception_handler_have_handler_for_exception():
    @exception_handler(handlers=test_handlers)
    def func():
        raise AttributeError()

    assert func() == HANDLED_ATTRIBUTE_ERROR


def test_exception_handler_have_handler_for_exception_func_throw_twice():
    @exception_handler(handlers=test_handlers)
    def func():
        raise RepeatedError()

    with pytest.raises(MaxRepeatedExceptionsError):
        func()


def test_exception_handler_have_no_handler():
    @exception_handler(handlers=test_handlers)
    def func():
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        func()


def test_exception_handler_default_return():
    @exception_handler(handlers=test_handlers, default_return=DEFAULT_RETURN)
    def func():
        raise RuntimeError()

    assert func() == DEFAULT_RETURN


def test_exception_handler_side_effect_handler(caplog):
    caplog.at_level(logging.WARNING)

    call_count = 0

    @exception_handler(handlers=test_handlers)
    def func():
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            raise LogThisError
        else:
            raise AttributeError

    assert func() == HANDLED_ATTRIBUTE_ERROR
    assert HANDLED_LOGGING in caplog.messages[0]


def test_exception_handler_two_different_exceptions():
    call_count = 0

    @exception_handler(handlers=test_handlers, max_repeated_exceptions=2)
    def func():
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            raise RetryThisError
        else:
            raise AttributeError

    assert func() == HANDLED_ATTRIBUTE_ERROR


def test_is_exceeded_max_repeated_exceptions_positive():
    assert is_exceeded_max_repeated_exceptions(
        ValueError,
        defaultdict(list, {ValueError: [1, 1]}),
        1
    ) is True


def test_is_exceeded_max_repeated_exceptions_negative():
    assert is_exceeded_max_repeated_exceptions(
        ValueError,
        defaultdict(list, {ValueError: [1]}),
        1
    ) is False
