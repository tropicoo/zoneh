"""Zone-H API Client."""

import logging
import os
import pickle
from io import BytesIO

import js2py
import requests

from zoneh.const import (
    TMP_DIR, MIRROR_URL, BASE_URL, HEADERS, COOKIES_JS_NAME, ARCHIVE_TYPES,
    COOKIES_JS_URL, CAPTCHA_URL, HZ_URL, Http
)
import zoneh.exceptions as exc
from zoneh.conf import get_config
from zoneh.parsers.htmlparser import HTMLParser
from zoneh.utils import get_randoma_ua, get_captcha_number, SingletonMeta

_CONF = get_config()


class Cookies:
    """Class to manage session cookies."""

    def __init__(self, api, session):
        """Class constructor."""
        self._api = api
        self._session = session
        self._parser = HTMLParser()
        self._cookie_file = None
        self._log = logging.getLogger(self.__class__.__name__)

    def init_cookies(self, force=False):
        """Init cookies."""
        if force:
            self._purge_cookies()
        if not self._session.cookies:
            self._initialize_cookies()

    def _initialize_cookies(self):
        """Really init cookies."""
        self._log.debug('Initializing cookies')
        self._cookie_file = f'{TMP_DIR}zoneh_cookiejar'
        if not self._load_cookies():
            self._prepare_cookies()

    def _load_cookies(self):
        """Load cookies from the file."""
        if os.path.isfile(self._cookie_file) and \
                os.stat(self._cookie_file).st_size > 0:
            with open(self._cookie_file, 'rb') as fd:
                self._session.cookies.update(pickle.load(fd))
            self._log.info('Cookies from %s loaded', self._cookie_file)
            return True
        return False

    def _purge_cookies(self):
        """Purge cookies file."""
        self._log.info('Purging cookies')
        with open(self._cookie_file, 'w'):
            pass

    def _save_cookies(self):
        """Save cookies to the file."""
        with open(self._cookie_file, 'wb') as fd:
            pickle.dump(self._session.cookies, fd)
        self._log.info('Cookies saved to %s', self._cookie_file)

    def _validate_cookies(self, cookies):
        """Validate cookies with API call."""
        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)
        text = self._api._request(HZ_URL.format(url=BASE_URL)).text
        return not self._parser.is_prelogin(text)

    def _prepare_cookies(self):
        """Prepare cookies."""
        cookies = self._get_cookies()
        if self._validate_cookies(cookies):
            self._save_cookies()
        else:
            # TODO: raise something
            pass

    def _get_cookies(self):
        """Generate cookies by evaluating js-functions from Zone-H website."""
        preload_page = self._api._request(BASE_URL).text
        js_aes_slow = self._api._request(COOKIES_JS_URL).text

        js_funcs, cookies = self._parser.parse_cookies(preload_page)
        value = js2py.eval_js('\n'.join([js_aes_slow, js_funcs]))
        cookies[COOKIES_JS_NAME] = value
        return cookies


class ZoneHAPI(metaclass=SingletonMeta):
    """Zone-H API class."""

    def __init__(self):
        """Class constructor."""
        self._session = requests.Session()
        self._session.headers.update(HEADERS)
        self._cookies = Cookies(self, self._session)
        self._random_ua = _CONF['zoneh']['random_ua']
        self._parser = HTMLParser()
        self._log = logging.getLogger(self.__class__.__name__)

    def init_cookies(self, force=False):
        """Init cookies."""
        self._cookies.init_cookies(force=force)

    def get_page(self, page_num, type_):
        """Get Zone-H html-page for parsing by its type."""
        page_url = ARCHIVE_TYPES[type_]['page']
        return self._request(page_url.format(page_num=page_num)).text

    def get_mirror_page(self, mirror_id):
        """Get Zone-H mirror html-page."""
        return self._request(MIRROR_URL.format(mirror_id=mirror_id)).text

    def get_captcha_img(self):
        """Get captcha image."""
        url = CAPTCHA_URL.format(captcha_num=get_captcha_number())
        return BytesIO(self._request(url).content)

    def solve_captcha(self, text, page):
        """Solve captcha by posting captcha's text."""
        self._log.info('Solving captcha with text "%s", page %s', text, page)
        self._log.debug('Cookies: %s', self._session.cookies.get_dict())
        url = ARCHIVE_TYPES[page[0]]['page'].format(page_num=page[1])
        res = self._request(method=Http.POST, url=url, data={'captcha': text})
        return not self._parser.is_captcha(res.content)

    def _request(self, url, method=Http.GET, data=None):
        """General request method."""
        self._log.debug('%s: %s %s', method, url, data)
        self._update_headers()
        try:
            res = self._session.request(method, url=url, data=data)
            self._verify_result(res)
        except Exception:
            err_msg = 'Issue with request to Zone-H'
            self._log.exception(err_msg)
            raise exc.ZoneHError(err_msg)
        return res

    @staticmethod
    def _verify_result(result):
        """Verify `requests` result."""
        return result

    def _update_headers(self):
        """Update headers with random User-Agent before API call."""
        if self._random_ua:
            headers = HEADERS
            headers['User-Agent'] = get_randoma_ua()
            self._log.debug('Random UA: %s', headers['User-Agent'])
            self._session.headers.update(headers)
