'''TODO'''
import inspect
import logging
from functools import wraps


def func_wrapper(func, logger=None):
    """TODO"""
    if logger is None:
        logger = logging.getLogger(__name__)

    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        caller = inspect.currentframe().f_back.f_code.co_name
        logger.debug(
            "caller='%s':called='%s':ret='%s'", caller, func.__name__, result
        )
        return result
    return inner


def cls_func_wrapper(function_wrapper, logger=None):
    """TODO"""
    if logger is None:
        logger = logging.getLogger(__name__)

    @wraps(function_wrapper)
    def inner(cls):
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            setattr(cls, name, function_wrapper(func, logger=logger))
        return cls
    return inner
