from zoneh.conf import get_config
from zoneh.const import FilterType
from zoneh.filters._base import BaseFilter
from zoneh.filters._registry import FilterRegistry

_CONF = get_config()


class NotifierFilter(BaseFilter, metaclass=FilterRegistry):

    TYPE = FilterType.NOTIFIER

    def __init__(self):
        super().__init__()
        self._notifiers = frozenset(_CONF['zoneh']['filters']['notifiers'])
        self.is_empty = bool(self._notifiers)

    def match(self, record):
        return record['notifier'] in self._notifiers
