import logging
from collections import defaultdict
from functools import wraps
from typing import DefaultDict, Union, ParamSpec, Any, Callable, Dict, Optional, Type, List, TypeVar

from read_env import read_env_as_int

DEFAULT_MAX_REPEATED_EXCEPTIONS = 1
UNSET_DEFAULT_RETURN: str = '__unset_default_return__'
EXCEPTION_OCCURRENCE: int = 1
MAX_REPEATED_EXCEPTIONS = (read_env_as_int('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS')
                           or DEFAULT_MAX_REPEATED_EXCEPTIONS)

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')
HandlerFuncType = Callable[..., Any]


class MaxRepeatedExceptionsError(Exception):
    pass


def exception_handler(
    handlers: Dict[Type[Exception], HandlerFuncType],
    default_return: Optional[Any] = UNSET_DEFAULT_RETURN,
    max_repeated_exceptions: int = MAX_REPEATED_EXCEPTIONS,
    occurred_exceptions: Optional[DefaultDict[Type[Exception], List[int]]] = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorate(func: Callable[P, T]) -> Callable[P, T]:

        nonlocal max_repeated_exceptions
        nonlocal occurred_exceptions

        if occurred_exceptions is None:
            occurred_exceptions = defaultdict(list)

        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Union[T, Any]:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                exc_type = type(exc)

                # per mypy guidance  on optional args https://mypy.readthedocs.io/en/stable/kinds_of_types.html
                assert occurred_exceptions is not None
                occurred_exceptions[exc_type].append(EXCEPTION_OCCURRENCE)

                if is_exceeded_max_repeated_exceptions(exc_type, occurred_exceptions, max_repeated_exceptions):
                    raise MaxRepeatedExceptionsError(
                        f'Exception {exc_type} exceeded max allowed occurrences of {max_repeated_exceptions}'
                    )
                if handler := get_handler_for_exception(handlers, exc):
                    logger.debug(f'Exception_handler: found handler {handler} for exception {repr(exc)}.')
                    print(handler)
                    return handler(
                        exception_handler(
                            handlers=handlers,
                            default_return=default_return,
                            max_repeated_exceptions=max_repeated_exceptions,
                            occurred_exceptions=occurred_exceptions
                        )(func), *args, **kwargs)

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
    return handlers.get(type(exc))


def is_exceeded_max_repeated_exceptions(
    exc: Type[Exception],
    occurred_exception: DefaultDict[Type[Exception], List[int]],
    max_repeated_exceptions: int
) -> bool:
    return len(occurred_exception.get(exc, [])) == max_repeated_exceptions + 1
