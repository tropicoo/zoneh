"""Zone-H module."""

import csv
import io
import logging
from collections import deque
from functools import wraps
from threading import Thread, Event

from telegram import Bot, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.utils.request import Request

import zoneh.exceptions
from zoneh.conf import get_config
from zoneh.formatter import Formatter
from zoneh.processor import Processor
from zoneh.utils import shallow_sleep, get_lock

_CONF = get_config()


def authorization_check(func):
    """Check that user is authorized to interact with bot."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        bot, update = args
        try:
            if update.message.chat.id not in bot._user_ids:
                raise zoneh.exceptions.UserAuthError
            return func(*args, **kwargs)
        except zoneh.exceptions.UserAuthError:
            bot._log.error('User authorization error')
            bot._log.error(bot._get_user_info(update))
            bot._print_access_error(update)

    return wrapper


class ZoneHBot(Bot):
    """Class where main bot things are done."""

    def __init__(self, stop_polling):
        token = _CONF['telegram']['token']
        super(ZoneHBot, self).__init__(token,
                                       request=(Request(con_pool_size=10)))
        self._log = logging.getLogger(self.__class__.__name__)
        self._user_ids = _CONF['telegram']['allowed_user_ids']
        self._stop_polling = stop_polling
        self._log.info('Initializing %s bot', self.first_name)

        self._captcha_queue = deque()
        self._pusher_on = Event()
        self._processor = Processor(captcha_queue=self._captcha_queue)
        self._lock = get_lock()

    def send_startup_message(self):
        """Send welcome message after bot launch."""
        self._log.info('Sending welcome message')

        for user_id in self._user_ids:
            self.send_message(user_id, '{0} bot started, see /help for '
                                       'available commands'.format(self.first_name))

    @authorization_check
    def cmds(self, update):
        """Print bot commands."""
        self._print_helper(update)

    @authorization_check
    def cmd_run(self, update):
        """Start scraping."""
        try:
            self._start_pusher(update)
        except zoneh.exceptions.ZoneHError as err:
            update.message.reply_text(str(err))
        except Exception:
            err_msg = 'Failed to start scraping'
            self._log.exception(err_msg)
            update.message.reply_text(err_msg)

    @authorization_check
    def cmd_stop(self, update):
        """Terminate bot."""
        msg = 'Stopping {0} bot'.format(self.first_name)
        self._log.info(msg)
        self._log.debug(self._get_user_info(update))
        self._stop_processor()
        update.message.reply_text(msg)
        thread = Thread(target=self._stop_polling)
        thread.start()

    @authorization_check
    def cmd_help(self, update):
        """Send help message to telegram chat."""
        self._log.info('Help message has been requested')
        self._log.debug(self._get_user_info(update))
        update.message.reply_text(
            'Use /run to run data gathering\n'
            'Use /stop command to fully stop the bot')
        self._log.info('Help message has been sent')

    @authorization_check
    def make_csv(self, update):
        """Make csv from all gathered records during bot run."""
        fd = io.StringIO()
        headers = []
        writer = None
        with self._lock:
            for rec in self._processor.temp_queue:
                if not headers:
                    headers = list(rec.keys())
                    writer = csv.DictWriter(fd, fieldnames=headers,
                                            dialect='excel')
                    writer.writeheader()
                writer.writerow(rec)
        csv_data = fd.getvalue().encode('utf-8')
        self.send_document(chat_id=update.message.chat.id,
                           document=io.BytesIO(csv_data),
                           caption='csv data',
                           filename='records.csv')

    def _stop_processor(self):
        self._processor.stop()

    def _start_pusher(self, update):
        if self._pusher_on.is_set():
            raise zoneh.exceptions.PusherError('Already running')
        self._processor.start()
        self._pusher_on.set()
        thread1 = Thread(target=self._pusher_worker, args=(update,))
        thread1.start()
        thread2 = Thread(target=self._captcha_worker, args=(update,))
        thread2.start()

    @authorization_check
    def solve_captcha(self, update):
        if self._processor.need_to_solve_captcha():
            self._processor.solve_captcha(update.message.text)

    def _captcha_worker(self, update):
        while self._pusher_on.is_set():
            with self._lock:
                while self._captcha_queue:
                    try:
                        captcha = self._captcha_queue.pop()
                        update.message.reply_photo(photo=captcha[0],
                                                   caption=captcha[1])
                    except IndexError:
                        pass
                    except Exception:
                        self._log.exception('Captcha worker error')
                    shallow_sleep(0.5)
            shallow_sleep(0.5)

    def _stop_pusher(self):
        if not self._pusher_on.is_set():
            raise zoneh.exceptions.PusherError('Already stopped')
        self._pusher_on.clear()

    def _pusher_worker(self, update):
        rec_num = 0
        while self._pusher_on.is_set():
            with self._lock:
                while self._processor.push_queue:
                    try:
                        record = self._processor.push_queue.pop()
                        rec_num += 1
                        formatter = Formatter(record, rec_num)
                        rec_formatted = formatter.format()
                        keyboard = [[InlineKeyboardButton('Open mirror',
                                                          url=formatter.get_mirror_url())]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_html(rec_formatted,
                                                  reply_markup=reply_markup)
                    except IndexError:
                        pass
                    shallow_sleep(1)
            shallow_sleep(1)

    def error_handler(self, update, error):
        """Handle known telegram bot API errors."""
        self._log.exception('Got error: %s', error)

    def _print_helper(self, update):
        """Send help message."""
        self.cmd_help(update)

    def _print_access_error(self, update):
        """Send authorization error to telegram chat."""
        update.message.reply_text('Not authorized')

    def _get_user_info(self, update):
        """Return user information who interacts with bot."""
        return 'Request from user_id: {0}, username: {1},' \
               'first_name: {2}, last_name: {3}'.format(
                                                update.message.chat.id,
                                                update.message.chat.username,
                                                update.message.chat.first_name,
                                                update.message.chat.last_name)
