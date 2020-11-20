from zoneh.conf import get_config
from zoneh.const import FilterType
from zoneh.filters._base import BaseFilter
from zoneh.filters._registry import FilterRegistry
from zoneh.iso3166 import COUNTRY_DICT

_CONF = get_config()


class CountryFilter(BaseFilter, metaclass=FilterRegistry):

    TYPE = FilterType.COUNTRY

    def __init__(self):
        super().__init__()
        _countries = _CONF['zoneh']['filters']['countries']
        self._countries = frozenset(COUNTRY_DICT[x] for x in _countries)
        self.is_empty = bool(self._countries)

    def match(self, record):
        pass
