"""Scraper module."""

import logging
import os
import pickle
from collections import deque
from io import BytesIO

import js2py
import requests

import zoneh.const as const
import zoneh.exceptions
from zoneh.conf import get_config
from zoneh.htmlparser import HTMLParser
from zoneh.utils import shallow_sleep, sleep_time, get_captcha_number, \
    get_randoma_ua

_LOG = logging.getLogger(__name__)
_CONF = get_config()


class Scraper:
    """Zone-H Scraper class."""

    def __init__(self, captcha_queue):
        """Class constructor."""
        self._session = requests.Session()
        self._session.headers.update(const.HEADERS)
        self._parser = HTMLParser()
        self._captcha_queue = captcha_queue
        self.got_captcha = False
        self._captcha_page = (None, None)
        self._cookie_file = None
        self._random_ua = _CONF['zoneh']['random_ua']

    def _initialize_cookies(self):
        _LOG.debug('Initializing cookies')
        self._cookie_file = '{0}zoneh_cookiejar'.format(const.TMP_DIR)

        if os.path.isfile(self._cookie_file) and \
                os.stat(self._cookie_file).st_size > 0:
            with open(self._cookie_file, 'rb') as fd:
                self._session.cookies.update(pickle.load(fd))
            _LOG.info('Cookies from %s loaded', self._cookie_file)
        else:
            self._set_cookies()

    def _purge_cookies(self):
        _LOG.info('Purging cookies')
        with open(self._cookie_file, 'w'):
            pass

    def _save_cookies(self):
        with open(self._cookie_file, 'wb') as fd:
            pickle.dump(self._session.cookies, fd)
        _LOG.info('Cookies saved to {0}', self._cookie_file)

    def _set_cookies(self):
        preload_page = self._make_request(const.BASE_URL).text
        js_aes_slow = self._make_request(const.COOKIES_JS_URL).text

        js_funcs, cookies = self._parser.parse_cookies(preload_page)
        value = js2py.eval_js('\n'.join([js_aes_slow, js_funcs]))
        cookies[const.COOKIES_JS_NAME] = value

        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)
        res = self._make_request(const.HZ_URL.format(url=const.BASE_URL))
        if self._parser.is_prelogin(res.text):
            # TODO
            pass
        else:
            self._save_cookies()

    def _get_advanced_data(self, mirror_id):
        res = self._make_request(const.MIRROR_URL.format(mirror_id=mirror_id))
        return self._parser.get_advanced_data(res.text)

    def get_archive(self, _type, start=None):
        page_url = const.ARCHIVE_TYPES[_type]['page']
        domains = _CONF['zoneh']['filters']['domains']
        if not self._session.cookies:
            self._initialize_cookies()
        try:
            page_queue = deque([start or const.START_PAGE])
            while page_queue:
                page_num = page_queue.pop()
                page = self._make_request(page_url.format(page_num=page_num))
                next_page = None
                for record, next_page in self._parser.get_records(page.content):
                    url = record['defaced_url']
                    if all([domains, '...' in url, '/' not in url]):
                        data = self._get_advanced_data(record['mirror'])
                        record['defaced_url'] = data['defaced_url_full']
                        shallow_sleep(sleep_time())
                    yield record
                if next_page:
                    page_queue.appendleft(next_page)
                shallow_sleep(sleep_time())
        except zoneh.exceptions.HTMLParserCaptchaRequest:
            self._send_captcha()
            self.got_captcha = True
            self._captcha_page = (_type, page_num)
            while self.got_captcha:
                shallow_sleep(1)
            yield from self.get_archive(_type, page_num)
        except zoneh.exceptions.HTMLParserCookiesError:
            self._purge_cookies()
            self._initialize_cookies()
            yield from self.get_archive(_type, page_num)
        except Exception:
            err_msg = 'Exception during getting record'
            _LOG.exception(err_msg)
            raise zoneh.exceptions.ScraperError(err_msg)

    def solve_captcha(self, captcha_text):
        url = const.ARCHIVE_TYPES[self._captcha_page[0]]['page'].format(
            page_num=self._captcha_page[1])
        res = self._make_request(method='POST', url=url,
                                 data={'captcha': captcha_text})

        if self._parser.is_captcha(res.content):
            self._send_captcha('Try again')
        else:
            self.got_captcha = False

    def _send_captcha(self, msg='Captcha request'):
        url = const.CAPTCHA_URL.format(captcha_num=get_captcha_number())
        captcha_res = self._make_request(url)
        self._captcha_queue.appendleft((BytesIO(captcha_res.content), msg))

    # TODO: Retry decorator
    def _make_request(self, url, method='GET', data=None):
        try:
            _LOG.debug('URL: %s', url)
            if self._random_ua:
                headers = const.HEADERS
                headers['User-Agent'] = get_randoma_ua()
                _LOG.debug('Random UA: %s', headers['User-Agent'])
                self._session.headers.update(headers)

            res = self._session.request(method, url=url, data=data)
            self._verify_result(res)
        except Exception:
            err_msg = 'Issue with request to Zone-H'
            _LOG.exception(err_msg)
            raise zoneh.exceptions.ZoneHError(err_msg)
        return res

    def _verify_result(self, result):
        # TODO
        return result
