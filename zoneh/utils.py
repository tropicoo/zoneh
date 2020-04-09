"""Utils module."""

import inspect
import logging
import secrets
import time
from threading import Lock

from fake_useragent import UserAgent

_log = logging.getLogger(__name__)
_UA = UserAgent(cache=True)
_LOCK = Lock()


class SingletonMeta(type):
    """SingletonMeta class."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Check whether instance already exists.

        Return existing or create new instance and save to dict."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def shallow_sleep(seconds=1):
    """Basic sleep function."""
    time.sleep(seconds)


def make_bold(text):
    """Make text bold before sending to the telegram chat."""
    return f'<b>{text}</b>'


def get_func_name():
    """Get function name."""
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    return calframe[1][3]


def get_captcha_number():
    """Get random number for captcha URL."""
    return secrets.choice(range(1, 1001))


def sleep_time():
    """Lowering the values increases the risk of getting perm banned
    by Zone-H's anti-DDoS logic.
    """
    return secrets.choice(range(7, 12))


def is_generator(func):
    """Check whether object is generator."""
    return inspect.isgeneratorfunction(func)


def get_randoma_ua():
    """Get random User-Agent."""
    return _UA.random


def get_lock():
    """Get thread lock."""
    return _LOCK
