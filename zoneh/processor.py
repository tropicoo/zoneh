"""Processor module."""

import json
import logging
import time
from collections import deque
from threading import Thread, Event

import zoneh.exceptions
from zoneh.conf import get_config
from zoneh.filters import Filter
from zoneh.scraper import Scraper
from zoneh.utils import shallow_sleep

CONF = get_config()


class Processor:
    def __init__(self, captcha_queue):
        self._log = logging.getLogger(self.__class__.__name__)
        self.push_queue = deque()
        self.temp_queue = deque(maxlen=10000)
        self._scraper = Scraper(captcha_queue=captcha_queue)
        self._filter = Filter()
        self._arch_type = CONF['zoneh']['archive']
        self._rescan_period = CONF['zoneh']['rescan_period']
        self._processor_on = Event()

    def need_to_solve_captcha(self):
        return self._scraper.got_captcha

    def solve_captcha(self, captcha_text):
        self._scraper.solve_captcha(captcha_text)

    def start(self):
        if self._processor_on.is_set():
            raise zoneh.exceptions.ProcessorError('Already running')
        self._processor_on.set()
        thread = Thread(target=self._worker)
        thread.start()

    def stop(self):
        if not self._processor_on.is_set():
            raise zoneh.exceptions.ProcessorError('Already stopped')
        self._processor_on.clear()

    def _worker(self):
        while self._processor_on.is_set():
            try:
                for record in self._scraper.get_archive(_type=self._arch_type):
                    if self._processor_on.is_set() and record not in self.temp_queue:
                        self._log.debug(json.dumps(record))
                        self.temp_queue.appendleft(record)
                        if self._filter.satisfy(record):
                            self.push_queue.appendleft(record)
                    else:
                        break
                time_delta = int(time.time()) + self._rescan_period
                while int(time.time()) < time_delta:
                    if not self._processor_on.is_set():
                        break
                    shallow_sleep(0.5)

            except Exception as err:
                err_msg = 'Processor thread received error ' \
                          'during handling scrape records'
                self._log.exception(err_msg)
                raise zoneh.exceptions.ProcessorError(err)
