Exception Handler decorator allows developers to specify specific exception types
to handle and provide a handler function for each of those exception
types. The decorator also provides an option to specify a default
return value to be used when an unhandled exception occurs. 
Additionally, the decorator tracks the number of times each 
exception type has been seen and raises a MaxRepeatedExceptionsError
when a specific exception type exceeds a specified maximum number of
occurrences.

Installation:
```shell
pip install exception-handler-plus
```


The decorator uses the exception_handler function as a wrapper 
for the decorated function. The function accepts four parameters:

- handlers (Dict[Type[Exception], HandlerFuncType]): A dictionary 
where the keys are exception types and the values are the corresponding
- handler functions for those exception types.
- default_return (Optional[Any]): A default return value to be 
used when an unhandled exception occurs.
- max_repeated_exceptions (int): The maximum number of times an 
exception type can be seen before a MaxRepeatedExceptionsError is 
raised.
- seen_exceptions (Optional[DefaultDict[Type[Exception], List[int]]]): 
A defaultdict used to keep track of the number of times each 
exception type has been seen.


The read_env module is used to read the maximum number of repeated 
exceptions that can occur from an environment variable.

Basic usage:
```python
import logging
from typing import Callable

from exception_handler_plus import exception_handler

logger = logging.getLogger(__name__)


def type_error_handler(func: Callable, *args, **kwargs):
    logger.error(f"Attribute Error occurred while calling {func} with arguments {args}, {kwargs}.")


handlers = {
    ValueError: lambda *_: "Handled Value Error",
    TypeError: type_error_handler

}


@exception_handler(handlers)
def my_function(x: int) -> int:
    if x < 0:
        raise ValueError
    if type(x) is not int:
        raise TypeError

    return x


my_function(-1)
# >>> 'Handled Value Error'
my_function("string")
# >>> Attribute Error occurred while calling <function my_function at 0x7f8db018d940> with arguments ('string',), {}.
```
