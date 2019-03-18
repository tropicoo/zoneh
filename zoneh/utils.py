"""Utils module."""
import inspect
import logging
import secrets
import time
from threading import Lock

from fake_useragent import UserAgent

_LOG = logging.getLogger(__name__)
_UA = UserAgent(cache=False)
_LOCK = Lock()


def shallow_sleep(secs):
    time.sleep(secs)


def create_csv_obj(data):
    pass


def make_bold(text):
    return f'<b>{text}</b>'


def get_fn_name():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    return calframe[1][3]


def get_captcha_number():
    return secrets.choice(range(1, 1001))


def sleep_time():
    """
    Lowering the values increases the risk of getting perm banned by Zone-H's
    anti-DDoS logic.
    """
    return secrets.choice(range(4, 7))


def is_generator(func):
    return inspect.isgeneratorfunction(func)


def get_randoma_ua():
    return _UA.random


def get_lock():
    return _LOCK
