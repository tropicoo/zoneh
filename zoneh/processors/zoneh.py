"""Processor module."""

import logging
from collections import deque
from threading import Event

from zoneh.conf import get_config

CONF = get_config()


class Processor:
    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self.push_queue = deque()
        self.temp_queue = deque(maxlen=10000)
        self._processor_on = Event()
