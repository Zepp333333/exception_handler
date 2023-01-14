Exception Handler decorator allows developers to specify specific exception types
to handle and provide a handler function for each of those exception
types. The decorator also provides an option to specify a default
return value to be used when an unhandled exception occurs. 
Additionally, the decorator tracks the number of times each 
exception type has been seen and raises a MaxRepeatedExceptionsError
when a specific exception type exceeds a specified maximum number of
occurrences.

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
