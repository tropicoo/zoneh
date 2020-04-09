"""Pusher threads module."""

import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from zoneh.captcha import captcha
from zoneh.commons import CommonThread
from zoneh.conf import get_config
from zoneh.parsers.formatter import FormattedRecord
from zoneh.utils import shallow_sleep, get_lock

CONF = get_config()


class PusherThread(CommonThread):
    """Pusher Thread Class."""

    def __init__(self, push_queue, update):
        super().__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self._update = update
        self._lock = get_lock()
        self._push_queue = push_queue

    def _run(self, ):
        rec_num = 0
        while self._run_trigger.is_set():
            with self._lock:
                self._log.debug('Captcha is active: %s', captcha.is_active)
                self._log.debug('Captcha is sent: %s', captcha.is_sent)
                if captcha.is_active and not captcha.is_sent:
                    self._send_captcha(self._update)

                while self._push_queue:
                    try:
                        record = self._push_queue.pop()
                    except IndexError:
                        pass

                    rec_num += 1
                    self._process_record(record, rec_num)
                    shallow_sleep(1)
            shallow_sleep(1)

    def _send_captcha(self, update):
        self._log.info('Sending captcha image to telegram')
        update.message.reply_photo(photo=captcha.image, caption=captcha.caption)
        captcha.is_sent = True

    def _process_record(self, record, rec_num):
        rec_formatted = FormattedRecord(record, rec_num)
        keyboard = [[InlineKeyboardButton(
            'Open mirror', url=rec_formatted.get_mirror_url())]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self._update.message.reply_html(rec_formatted.data,
                                        reply_markup=reply_markup)
