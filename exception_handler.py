import logging
import os
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, List, TypeVar, Union

UNSET_DEFAULT_RETURN = '__unset_default_return__'
OCCURRENCE = 1
MAX_REPEATED_EXCEPTIONS = os.getenv('EXCEPTION_HANDLER_MAX_REPEATED_EXCEPTIONS') or 1

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

HandlerFuncType = Union[
    Callable[[Any, ...], Any],
]


class MaxRepeatedExceptionsError(Exception):
    pass


def exception_handler(
    handlers: Dict[Type[Exception], HandlerFuncType],
    default_return: Optional[Any] = UNSET_DEFAULT_RETURN,
    max_repeated_exceptions: int = MAX_REPEATED_EXCEPTIONS,
    occurred_exceptions: defaultdict[Type[Exception], List[int]] = None
):
    def decorate(func: Callable):

        nonlocal max_repeated_exceptions
        nonlocal occurred_exceptions

        if occurred_exceptions is None:
            occurred_exceptions = defaultdict(list)

        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                exc_type = type(exc)
                occurred_exceptions[exc_type].append(OCCURRENCE)

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
    occurred_exception: defaultdict[Type[Exception], List[int]],
    max_repeated_exceptions: int
) -> bool:
    return len(occurred_exception.get(exc, [])) == max_repeated_exceptions + 1
