"""Zone-H captcha module."""

import logging
from collections import deque

from zoneh.clients.zoneh import ZoneHAPI
from zoneh.conf import get_config
from zoneh.decorators import lock
from zoneh.exceptions import CaptchaError
from zoneh.parsers.htmlparser import HTMLParser
from zoneh.utils import SingletonMeta

_CONF = get_config()


class Captcha(metaclass=SingletonMeta):
    """Shared object representing real captcha."""

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)
        self.caption = 'Captcha request'
        self.err_msg = 'Try once more'
        self._image = None
        self._is_active = False
        self._is_sent = False
        self.failed_attempts = 0
        self.page = None

    def __repr__(self):
        return f'Captcha'

    def reset(self):
        self.page = None
        self.failed_attempts = 0
        self._image = None
        self._is_active = False
        self._is_sent = False

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._log.debug('Setting image %s', image)
        self._image = image

    @property
    def is_sent(self):
        return self._is_sent

    @is_sent.setter
    def is_sent(self, is_sent):
        if is_sent and self._is_sent:
            raise CaptchaError('Captcha is already sent')
        elif not is_sent and not self._is_sent:
            raise CaptchaError('Captcha is already not sent')
        self._is_sent = is_sent

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        if is_active and self._is_active:
            err_msg = 'Captcha is already active'
            self._log.error(err_msg)
            raise CaptchaError(err_msg)
        elif not is_active and not self._is_active:
            err_msg = 'Captcha is already inactive'
            self._log.error(err_msg)
            raise CaptchaError(err_msg)
        self._is_active = is_active


class CaptchaManager(metaclass=SingletonMeta):

    def __init__(self, captcha_):
        self._log = logging.getLogger(self.__class__.__name__)
        self._api = ZoneHAPI()
        self._captcha = captcha_
        self._captcha_queue = deque()
        self._parser = HTMLParser()

    @lock
    def init_captcha(self, type_, page_num):
        captcha.is_active = True
        captcha.page = (type_, page_num)
        captcha.image = self._api.get_captcha_img()

    @lock
    def solve_captcha(self, captcha_text):
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
        self._log.info('Updating captcha')
        self._captcha.image = self._api.get_captcha_img()
        self._captcha.failed_attempts += 1

    def get_queue(self):
        return self._captcha_queue


captcha = Captcha()
captcha_manager = CaptchaManager(captcha)
