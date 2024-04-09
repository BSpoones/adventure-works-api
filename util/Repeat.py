from functools import wraps
from typing import Callable
from random import random as rand_float
import logging, asyncio, time

logger = logging.getLogger("AsyncRepeat")


def repeat(retries: int = 3, delay_secs: float = 0.5, max_delay_secs: float | None = None):
    """
    Writing python code is torture enough, I'll comment later

    :param retries: Integer amount of times to retry1
    :param delay_secs: Float amount of seconds to delay
    :param max_delay_secs: TODO -> COMMENT THIS LOL
    """
    def decorator(func: Callable):
        @wraps(func)  # Ensures docs transfer properly
        def wrapper(*args, **kwargs):
            exceptions = set()
            delay = delay_secs
            max_delay = max_delay_secs if max_delay_secs else delay * 10
            for i in range(1, retries - 1):
                logger.debug(f"Attempt: {i,} - {repr(func)}")
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries:
                        break

                    exceptions.add(repr(e))
                    time.sleep(_get_delay(delay, max_delay, i - 1))

            formatted_exceptions = "\n- ".join(exceptions)
            logger.critical(f"Attempt failed: {formatted_exceptions}")

        return wrapper

    return decorator


def _get_delay(delay, max_delay, iteration):
    """
    Adds delay + jitter

    Jitter? I hardly know her!

    :param delay:
    :param max_delay:
    :param iteration:
    :return:
    """
    delay *= 2 ** iteration
    return min(delay, max_delay) + rand_float()
