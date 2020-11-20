"""Processor module."""

import logging
from collections import deque
from threading import Event

from zoneh.const import MAX_DEQUE_ITEMS


class ZonehProcessor:
    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self.push_queue = deque()
        self.temp_queue = deque(maxlen=MAX_DEQUE_ITEMS)
        self._processor_on = Event()
