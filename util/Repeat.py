from functools import wraps
from typing import Callable
from random import random as rand_float
import logging, time

logger = logging.getLogger("Repeat")


def repeat(retries: int = 3, delay_secs: float = 0.5, max_delay_secs: float | None = None):
    """
    A decorator that repeats a function a select amount of times

    This is an extension to https://github.com/indently/five_decorators/blob/main/decorators/001_retry.py
    where I have added further error handling, as well as a scalable jitter, found in real life APIs
    """
    def decorator(func: Callable):
        @wraps(func)  # Ensures docs transfer properly
        def wrapper(*args, **kwargs):
            exceptions = set()
            delay = delay_secs
            max_delay = max_delay_secs if max_delay_secs else delay * 10
            for i in range(1, retries - 1):
                logger.debug(f"Attempt: {i:,} - {repr(func)}")
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries:
                        break

                    exceptions.add(repr(e))
                    # NOTE: This would be asyncio.sleep if the assignment allowed for asynchronous
                    # database connections
                    time.sleep(_get_delay(delay, max_delay, i - 1))

            formatted_exceptions = "\n- ".join(exceptions)
            logger.critical(f"Attempt failed: {formatted_exceptions}")

        return wrapper

    return decorator


def _get_delay(delay, max_delay, iteration):
    """
    Adds an exponential jitter for failed requests
    """
    delay *= 2 ** iteration
    return min(delay, max_delay) + rand_float()
