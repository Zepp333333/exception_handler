import logging
from collections import defaultdict
from functools import wraps
from typing import DefaultDict, Union, Any, Callable, Dict, Optional, Type, List, TypeVar

from read_env import read_env_as_int

DEFAULT_MAX_REPEATED_EXCEPTIONS = 1

UNSET_DEFAULT_RETURN: str = '__unset_default_return__'
EXCEPTION_OCCURRENCE: int = 1
MAX_REPEATED_EXCEPTIONS = (read_env_as_int('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS')
                           or DEFAULT_MAX_REPEATED_EXCEPTIONS)

T = TypeVar('T')
HandlerFuncType = Callable[[Callable[..., T], ...], Any]

logger = logging.getLogger(__name__)


class MaxRepeatedExceptionsError(Exception):
    """
    Custom exception class to raise when a certain exception has exceeded the maximum allowed occurrences.
    """
    pass


def exception_handler(
    handlers: Dict[Type[Exception], HandlerFuncType],
    default_return: Optional[Any] = UNSET_DEFAULT_RETURN,
    max_repeated_exceptions: int = MAX_REPEATED_EXCEPTIONS,
    seen_exceptions: Optional[DefaultDict[Type[Exception], List[int]]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    A decorator function that allows you to handle exceptions in a more organized and efficient way.
    :param handlers: A dictionary of exception types and the functions to handle them.
    :param default_return: The default return value when an exception is raised and no handler is found.
    :param max_repeated_exceptions: The maximum allowed occurrences of an exception before raising a
            MaxRepeatedExceptionsError.
    :param seen_exceptions: A defaultdict of the exception types and their occurrences.
    :return: The decorated function.
    """

    def decorate(func: Callable[..., T]) -> Callable[..., T]:

        nonlocal max_repeated_exceptions
        nonlocal seen_exceptions

        if seen_exceptions is None:
            seen_exceptions = defaultdict(list)

        @wraps(func)
        def wrapped(*args, **kwargs) -> Union[T, Any]:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                exc_type = type(exc)

                # per mypy guidance  on optional args https://mypy.readthedocs.io/en/stable/kinds_of_types.html
                assert seen_exceptions is not None
                seen_exceptions[exc_type].append(EXCEPTION_OCCURRENCE)

                if is_exceeded_max_repeated_exceptions(exc_type, seen_exceptions, max_repeated_exceptions):
                    raise MaxRepeatedExceptionsError(
                        f'Exception {exc_type} exceeded max allowed occurrences of {max_repeated_exceptions}'
                    )
                if handler := get_handler_for_exception(handlers, exc):
                    logger.debug(f'Exception_handler: found handler {handler} for exception {repr(exc)}.')
                    return handler(func, *args, **kwargs)

                else:
                    if default_return != UNSET_DEFAULT_RETURN:
                        logger.debug(f'Returned default value: {default_return} instead of raising {repr(exc)}')
                        return default_return
                    raise exc

        return wrapped

    return decorate


def get_handler_for_exception(
    handlers: Dict[Type[Exception], HandlerFuncType],
    exc: Exception
) -> Optional[HandlerFuncType]:
    """
    Given a dictionary of exception handlers, and an exception instance,
    returns the appropriate handler function for the exception.
    If no handler is found, returns None.
    """
    return handlers.get(type(exc))


def is_exceeded_max_repeated_exceptions(
    exc: Type[Exception],
    occurred_exception: DefaultDict[Type[Exception], List[int]],
    max_repeated_exceptions: int
) -> bool:
    """
    Given an exception type, a dictionary of occurred exceptions and their count,
    and a max number of allowed occurrences,
    returns True if the exception has exceeded the max allowed occurrences, False otherwise.
    """
    return len(occurred_exception.get(exc, [])) == max_repeated_exceptions + 1
