"""Processor threads module."""

import json
import logging
import time

import zoneh.exceptions as exc
from zoneh.commons import CommonThread
from zoneh.conf import get_config
from zoneh.filters.zoneh import Filter
from zoneh.scraper import Scraper
from zoneh.utils import shallow_sleep

CONF = get_config()


class ProcessorThread(CommonThread):
    """Processor Thread Class."""

    def __init__(self, push_queue, temp_queue):
        super().__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self._push_queue = push_queue
        self._temp_queue = temp_queue
        self._scraper = Scraper()
        self._filter = Filter()
        self._arch_type = CONF['zoneh']['archive']
        self._rescan_period = CONF['zoneh']['rescan_period']

    def _run(self):
        while self._run_trigger.is_set():
            try:
                self._pull_records()
            except Exception as err:
                err_msg = 'Processor thread received error ' \
                          'during handling scrape records'
                self._log.exception(err_msg)
                raise exc.ProcessorError(err)

            self._take_a_nap()

    def _pull_records(self):
        for record in self._scraper.get_archive(type_=self._arch_type):
            if not self._run_trigger.is_set() or record in self._temp_queue:
                break
            self._process_record(record)

    def _process_record(self, record):
        self._log.debug(json.dumps(record))
        self._temp_queue.appendleft(record)
        if self._filter.satisfy(record):
            self._push_queue.appendleft(record)

    def _take_a_nap(self):
        time_delta = int(time.time()) + self._rescan_period
        while int(time.time()) < time_delta:
            if not self._run_trigger.is_set():
                break
            shallow_sleep(0.5)
