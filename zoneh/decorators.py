"""Decorators module."""

from functools import wraps

import zoneh.exceptions as exc
from zoneh.utils import get_lock
from zoneh.utils import is_generator

_lock = get_lock()


def authorization_check(func):
    """Check that user is authorized to interact with bot."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        bot, update = args
        if update.message.chat.id in bot._user_ids:
            return func(*args, **kwargs)
        bot._log.error('User authorization error')
        bot._log.error(bot._get_user_info(update))
        bot._print_access_error(update)

    return wrapper


def lock(func):
    """Thread locking decorator.

    Caution: can create deadlock.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with _lock:
            return func(*args, **kwargs)

    return wrapper


def _content_handler_helper(parser, page):
    """Helper function to verify the fetched content."""
    if parser.is_captcha(page):
        warn_msg = 'Captcha request'
        parser._log.warning(warn_msg)
        raise exc.HTMLParserCaptchaRequest(warn_msg)
    elif parser.is_prelogin(page):
        err_msg = 'Pre-login page. Need to set cookies'
        parser._log.error(err_msg)
        raise exc.HTMLParserCookiesError(err_msg)
    else:
        err_msg = 'Couldn\'t find HTML element. Check logs'
        parser._log.exception(err_msg)
        raise exc.HTMLParserError(err_msg)


def content_handler(func):
    """HTML content handler decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        parser, page = args

        def iter_func():
            try:
                yield from func(*args, **kwargs)
            except Exception:
                _content_handler_helper(parser, page)

        try:
            return iter_func() if is_generator(func) else func(*args, **kwargs)
        except Exception:
            _content_handler_helper(parser, page)

    return wrapper
