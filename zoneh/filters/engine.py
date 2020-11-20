"""Filter engine module."""

import logging

from zoneh.conf import get_config
from zoneh.filters._registry import FilterRegistry

_CONF = get_config()


class FilterEngine:
    """Record Filter Engine."""

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)
        self._registry = FilterRegistry
        self._is_active = self._get_active_state()
        self._log.info('Initializing %s with filters %s', repr(self),
                       self._registry.get_instances())

    def __repr__(self):
        return f'<{self.__class__.__name__} is_active:{self._is_active}'

    def _get_active_state(self):
        return any([f.is_empty for f in self._registry.REGISTRY.values()])

    def match(self, record):
        """Check whether record matches any of the configured filters."""
        if not self._is_active:
            return True
        return any([f.match(record) for f in self._registry.REGISTRY.values()])
