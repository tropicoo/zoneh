"""Filter module."""

from urllib.parse import urlsplit

from zoneh.conf import get_config
from zoneh.iso3166 import COUNTRY_DICT

_CONF = get_config()


class Filter:
    def __init__(self):
        countries = _CONF['zoneh']['filters']['countries']
        self._countries = [COUNTRY_DICT[x] for x in countries]
        self._domains = _CONF['zoneh']['filters']['domains']
        self._notifiers = _CONF['zoneh']['filters']['notifiers']

    def satisfy(self, record):
        if not any([self._countries, self._domains, self._notifiers]):
            return True
        return any([record['country'] in self._countries,
                    self.__match_domains(record),
                    record['notifier'] in self._notifiers])

    def __match_domains(self, record):
        defaced_url = record['defaced_url']
        defaced_domain = urlsplit(defaced_url).netloc
        if not defaced_domain:
            defaced_url = 'http://{0}'.format(defaced_url)
            defaced_domain = urlsplit(defaced_url).netloc
        for domain in self._domains:
            if defaced_domain.endswith(domain):
                return True
        return False
