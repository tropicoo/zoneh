"""Scraper module."""

import logging
from collections import deque

import zoneh.const as const
import zoneh.exceptions as exc
from zoneh.captcha import captcha
from zoneh.clients.zoneh import ZoneHAPI
from zoneh.conf import get_config
from zoneh.managers.captcha import captcha_manager
from zoneh.parsers.htmlparser import HTMLParser
from zoneh.utils import shallow_sleep, sleep_time, get_lock

_log = logging.getLogger(__name__)
_CONF = get_config()


class Scraper:
    """Zone-H Website Scraper class."""

    def __init__(self):
        """Class constructor."""
        self._api = ZoneHAPI()
        self._parser = HTMLParser()
        self._lock = get_lock()

    def get_archive(self, type_, start=None):
        """Get archive from Zone-H by given archive type."""
        domains = _CONF['zoneh']['filters']['domains']
        self._api.init_cookies()
        page_queue = deque([start or const.START_PAGE])
        while page_queue:
            page_num = page_queue.pop()
            html_page = self._api.get_page(page_num, type_)
            next_page = None
            try:
                for record, next_page in self._parser.get_records(html_page):
                    url = record['defaced_url']
                    if all([domains, '...' in url, '/' not in url]):
                        data = self._get_advanced_data(record['mirror'])
                        record['defaced_url'] = data['defaced_url_full']
                        shallow_sleep(sleep_time())
                    yield record
            except exc.HTMLParserCaptchaRequest:
                captcha_manager.init_captcha(type_, page_num)
                while captcha.is_active:
                    shallow_sleep(1)
                yield from self.get_archive(type_, page_num)
            except exc.HTMLParserCookiesError:
                self._api.init_cookies(force=True)
                shallow_sleep(2)
                yield from self.get_archive(type_, page_num)
            except Exception:
                err_msg = 'Exception during getting record'
                _log.exception(err_msg)
                raise exc.ScraperError(err_msg)

            if next_page:
                page_queue.appendleft(next_page)
            shallow_sleep(sleep_time())

    def _get_advanced_data(self, mirror_id):
        """Get advanced data from Zone-H mirror page."""
        text = self._api.get_mirror_page(mirror_id)
        return self._parser.get_advanced_data(text)
