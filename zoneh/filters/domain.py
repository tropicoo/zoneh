from urllib.parse import urlsplit

from zoneh.conf import get_config
from zoneh.const import FilterType
from zoneh.filters._base import BaseFilter
from zoneh.filters._registry import FilterRegistry

_CONF = get_config()


class DomainFilter(BaseFilter, metaclass=FilterRegistry):
    TYPE = FilterType.DOMAIN

    def __init__(self):
        super().__init__()
        self._domain_parts = self.__normalize_parts()
        self.is_empty = bool(self._domain_parts)

    @staticmethod
    def __normalize_parts():
        domains = _CONF['zoneh']['filters']['domains']
        return tuple(x.lower() for x in domains)

    def match(self, record):
        return self._match_domains(record)

    def _match_domains(self, record):
        """Check whether record matches configured domain filter."""
        defaced_url = record['defaced_url']
        defaced_domain = urlsplit(defaced_url).netloc
        if not defaced_domain:
            defaced_domain = urlsplit(f'http://{defaced_url}').netloc
        for domain_part in self._domain_parts:
            if defaced_domain.endswith(domain_part):
                return True
        return False
