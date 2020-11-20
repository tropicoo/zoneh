"""Captcha manager module."""

import logging

from zoneh.captcha import captcha
from zoneh.clients.zoneh import ZoneHAPI
from zoneh.decorators import lock
from zoneh.parsers.htmlparser import HTMLParser
from zoneh.utils import Singleton


class CaptchaManager(metaclass=Singleton):
    """Captcha manager class."""

    def __init__(self, captcha_):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self._api = ZoneHAPI()
        self._captcha = captcha_
        self._parser = HTMLParser()

    @lock
    def init_captcha(self, type_, page_num):
        """Init captcha object."""
        captcha.is_active = True
        captcha.page = (type_, page_num)
        captcha.image = self._api.get_captcha_img()

    @lock
    def solve_captcha(self, captcha_text):
        """Solve captcha."""
        self._log.info('Solving captcha with text "%s"', captcha_text)
        self._captcha.is_sent = False
        if not self._api.solve_captcha(captcha_text, captcha.page):
            self._log.info('Captcha not solved')
            self._update_captcha()
            return False

        self._log.info('Captcha solved')
        self._captcha.reset()
        return True

    def _update_captcha(self):
        """Update captcha after failed solve attempt."""
        self._log.info('Updating captcha')
        self._captcha.image = self._api.get_captcha_img()
        self._captcha.failed_attempts += 1


captcha_manager = CaptchaManager(captcha)
