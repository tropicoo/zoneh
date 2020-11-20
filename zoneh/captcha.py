"""Zone-H captcha module."""

import logging

from zoneh.conf import get_config
from zoneh.exceptions import CaptchaError
from zoneh.utils import Singleton

_CONF = get_config()


class Captcha(metaclass=Singleton):
    """Shared object representing real captcha."""

    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self.caption = 'Captcha request, please type what you see'
        self.err_msg = 'Try once more'
        self._image = None
        self._is_active = False
        self._is_sent = False
        self.failed_attempts = 0
        self.page = None

    def __repr__(self):
        return f'Captcha'

    def reset(self):
        """Reset captcha states."""
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


captcha = Captcha()
