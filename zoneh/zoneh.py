"""Zone-H module."""

import logging
from threading import Event, Thread

from telegram import Bot
from telegram.utils.request import Request

import zoneh.exceptions as exc
from zoneh.captcha import captcha
from zoneh.conf import get_config
from zoneh.decorators import authorization_check
from zoneh.managers.captcha import captcha_manager
from zoneh.managers.thread import ThreadManager
from zoneh.processors.csv import CsvProcessor
from zoneh.processors.zoneh import ZonehProcessor
from zoneh.threads.processor import ProcessorThread
from zoneh.threads.pusher import PusherThread
from zoneh.utils import get_lock

_CONF = get_config()


class ZoneHBot(Bot):
    """Class where main bot things are done."""

    def __init__(self, stop_polling):
        """Class constructor."""
        token = _CONF['telegram']['token']
        super().__init__(token, request=(Request(con_pool_size=10)))
        self._log = logging.getLogger(self.__class__.__name__)
        self._user_ids = _CONF['telegram']['allowed_user_ids']
        self._stop_polling = stop_polling
        self._log.info('Initializing %s bot', self.first_name)

        self._pusher_on = Event()
        self._processor = ZonehProcessor()
        self._lock = get_lock()
        self._thread_manager = ThreadManager([])

    def send_welcome_message(self):
        """Send welcome message after bot launch."""
        self._log.info('Sending welcome message')

        for user_id in self._user_ids:
            self.send_message(user_id, f'{self.first_name} bot started, '
                                       f'see /help for available commands '
                                       f'or /run')

    @authorization_check
    def cmds(self, update):
        """Print bot commands."""
        self._print_helper(update)

    @authorization_check
    def cmd_run(self, update):
        """Start scraping."""
        try:
            self._start_threads(update)
        except exc.ZoneHError as err:
            update.message.reply_text(str(err))
        except Exception:
            err_msg = 'Failed to start scraping'
            self._log.exception(err_msg)
            update.message.reply_text(err_msg)

    @authorization_check
    def cmd_stop(self, update):
        """Terminate bot."""
        msg = f'Stopping {self.first_name} bot'
        self._log.info(msg)
        self._log.debug(self._get_user_info(update))

        self._thread_manager.stop_threads()
        update.message.reply_text(msg)

        thread = Thread(target=self._stop_polling, name='Stop polling thread')
        thread.start()

    @authorization_check
    def cmd_help(self, update):
        """Send help message to telegram chat."""
        self._log.info('Help message has been requested')
        self._log.debug(self._get_user_info(update))
        update.message.reply_text('Use /run to run data gathering\n'
                                  'Use /stop command to fully stop the bot')
        self._log.info('Help message has been sent')

    @authorization_check
    def make_csv(self, update):
        """Make csv from all gathered records during bot run."""
        with self._lock:
            csv_ = CsvProcessor()
            for rec in self._processor.temp_queue:
                csv_.write(rec)

        self.send_document(chat_id=update.message.chat.id,
                           document=csv_.get_data(),
                           caption='csv data',
                           filename='records.csv')

    def _start_threads(self, update):
        """Start core threads during bot start"""
        proc_thread = ProcessorThread(self._processor.push_queue,
                                      self._processor.temp_queue)
        pusher_thread = PusherThread(self._processor.push_queue, update)
        self._thread_manager = ThreadManager([proc_thread, pusher_thread])
        self._thread_manager.start_threads()

    @authorization_check
    def solve_captcha(self, update):
        """Solve captcha."""
        if not captcha.is_active:
            self._log.warning('Captcha inactive, skip solving')
            return

        self._log.info('Solving captcha')
        is_solved = captcha_manager.solve_captcha(update.message.text)
        update.message.reply_text(
            'Captcha solved' if is_solved else 'Try again')

    def error_handler(self, update, error):
        """Handle known telegram bot API errors."""
        self._log.exception('Got error: %s', error)

    def _print_helper(self, update):
        """Send help message."""
        self.cmd_help(update)

    @staticmethod
    def _print_access_error(update):
        """Send authorization error to telegram chat."""
        update.message.reply_text('Not authorized')

    @staticmethod
    def _get_user_info(update):
        """Return user information who interacts with bot."""
        return 'Request from user_id: {0}, username: {1},' \
               'first_name: {2}, last_name: {3}' \
            .format(update.message.chat.id,
                    update.message.chat.username,
                    update.message.chat.first_name,
                    update.message.chat.last_name)
