from collections import defaultdict

import pytest

from exception_handler.exception_handler import exception_handler, MaxRepeatedExceptionsError


class TestException(Exception):
    pass


class TestException2(Exception):
    pass


def test_specific_handler_called():
    # Test setup
    handlers = {TestException: lambda _: 1}

    @exception_handler(handlers=handlers)
    def test_function():
        raise TestException()

    # function call
    assert test_function() == 1


def test_default_value_returned():
    # Test setup
    handlers = {TestException: lambda x: x + 1}
    default_return = 'default_return'

    @exception_handler(handlers=handlers, default_return=default_return)
    def test_function():
        raise TestException2()

    # function call
    assert test_function() == 'default_return'


def test_exception_raised_when_no_handler_or_default():
    # Test setup
    handlers = {TestException: lambda x: x + 1}

    @exception_handler(handlers=handlers)
    def test_function():
        raise TestException2()

    # function call
    with pytest.raises(TestException2):
        test_function()


def test_max_repeated_exception_error_raised():
    # Test setup
    handlers = {TestException: lambda _: 1}
    max_repeated_exceptions = 1

    @exception_handler(handlers=handlers, max_repeated_exceptions=max_repeated_exceptions)
    def test_function():
        raise TestException()

    test_function()
    # function call
    with pytest.raises(MaxRepeatedExceptionsError):
        test_function()


def test_occurrences_tracked():
    # Test setup
    handlers = {TestException: lambda _: 1, TestException2: lambda _: 2}

    @exception_handler(handlers=handlers, max_repeated_exceptions=3)
    def test_function():
        raise TestException()

    test_function()
    test_function()
    test_function()
    with pytest.raises(MaxRepeatedExceptionsError):
        test_function()


def test_multiple_exception_types_and_handlers():
    # Test setup
    handlers = {TestException: lambda _:  1, TestException2: lambda _: 2}

    exceptions_count = 0
    @exception_handler(handlers=handlers)
    def test_function():
        nonlocal exceptions_count
        if exceptions_count == 0:
            exceptions_count +=1
            raise TestException()
        if exceptions_count == 1:
            exceptions_count +=1
            raise TestException2
        raise ValueError

    # function call
    assert test_function() == 1

    assert test_function() == 2

    with pytest.raises(ValueError):
        test_function()

def test_nested_function_calls_and_exception_types():
    # Test setup
    handlers = {TestException: lambda _: 1}

    @exception_handler(handlers=handlers)
    def test_function():
        def nested_function():
            raise TestException()

        return nested_function()

    # function call
    assert test_function() == 1


def test_keyword_arguments():
    # Test setup

    handlers = {TestException: lambda _, x, y: x+ y}

    @exception_handler(handlers=handlers)
    def test_function(x, y):
        raise TestException()

    # function call
    assert test_function(x=1, y=2) == 3


def test_non_exception_type():
    # Test setup
    handlers = {int: lambda x: x + 1}

    @exception_handler(handlers=handlers)
    def test_function():
        raise TypeError()

    # function call
    with pytest.raises(TypeError):
        test_function()


def test_empty_handlers_dict():
    # Test setup
    handlers = {}

    @exception_handler(handlers=handlers)
    def test_function():
        raise TestException()

    # function call
    with pytest.raises(TestException):
        test_function()


def test_none_default_return():
    # Test setup
    handlers = {TestException: lambda x: x + 1}
    default_return = None

    @exception_handler(handlers=handlers, default_return=default_return)
    def test_function():
        raise TestException2()

    # function call
    assert test_function() is None


def test_empty_occurred_exceptions_list():
    # Test setup
    handlers = {TestException: lambda _: 1}
    occurred_exceptions = defaultdict(list)

    @exception_handler(handlers=handlers, seen_exceptions=occurred_exceptions)
    def test_function():
        raise TestException()

    # function call
    test_function()
    assert occurred_exceptions == {TestException: [1]}
