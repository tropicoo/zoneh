#!/usr/bin/env python3
"""Bot launcher module."""

import logging

from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

import zoneh.const as const
from zoneh.conf import get_config
from zoneh.zoneh import ZoneHBot

_CONF = get_config()

__version__ = '0.2'


class ZBotLauncher:
    """Bot launcher."""

    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)

        log_level = self._get_int_log_level(_CONF['log_level'])
        logging.getLogger().setLevel(log_level)

        self._bot = ZoneHBot(stop_polling=self._stop_polling)
        self._updater = Updater(bot=self._bot)
        self._welcome_sent = False
        self._setup_commands()

    def run(self):
        """Run bot."""
        self._log.info('Starting %s bot', self._updater.bot.first_name)
        self._send_welcome_message()
        self._updater.start_polling()
        self._updater.idle()

    def _send_welcome_message(self):
        """Send welcome message to the user."""
        if not self._welcome_sent:
            self._updater.bot.send_welcome_message()
            self._welcome_sent = True

    def _stop_polling(self):
        """Stops bot and exits application."""
        self._updater.stop()
        self._updater.is_idle = False

    def _setup_commands(self):
        """Setup for Dispatcher with bot commands and error handler."""
        dispatcher = self._updater.dispatcher
        dispatcher.add_handler(CommandHandler('help', ZoneHBot.cmd_help))
        dispatcher.add_handler(CommandHandler('start', ZoneHBot.cmd_help))
        dispatcher.add_handler(CommandHandler('stop', ZoneHBot.cmd_stop))
        dispatcher.add_handler(CommandHandler('run', ZoneHBot.cmd_run))
        dispatcher.add_handler(CommandHandler('csv', ZoneHBot.make_csv))
        dispatcher.add_handler(
            MessageHandler(Filters.text, ZoneHBot.solve_captcha))
        dispatcher.add_error_handler(ZoneHBot.error_handler)

    def _get_int_log_level(self, log_level_str):
        if log_level_str not in const.LOG_LEVELS:
            warn_msg = f'Invalid log level "{log_level_str}", using "INFO". ' \
                       f'Choose from {const.LOG_LEVELS})'
            self._log.warning(warn_msg)
        return getattr(logging, log_level_str, logging.INFO)


if __name__ == '__main__':
    log_format = '%(asctime)s - [%(levelname)s] - [%(name)s:%(lineno)d] - %(message)s'
    logging.basicConfig(format=log_format)

    zoneh = ZBotLauncher()
    zoneh.run()
