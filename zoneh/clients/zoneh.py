"""Zone-H API Client."""

import logging
import os
import pickle
from io import BytesIO

import js2py
import requests

import zoneh.const as const
import zoneh.exceptions as exc
from zoneh.conf import get_config
from zoneh.parsers.htmlparser import HTMLParser
from zoneh.utils import get_randoma_ua, get_captcha_number, SingletonMeta

_CONF = get_config()


class Cookies:

    def __init__(self, api, session):
        self._api = api
        self._session = session
        self._parser = HTMLParser()
        self._cookie_file = None
        self._log = logging.getLogger(self.__class__.__name__)

    def init_cookies(self, force=False):
        if force:
            self._purge_cookies()
        if not self._session.cookies:
            self._initialize_cookies()

    def _initialize_cookies(self):
        self._log.debug('Initializing cookies')
        self._cookie_file = f'{const.TMP_DIR}zoneh_cookiejar'
        if not self._load_cookies():
            self._prepare_cookies()

    def _load_cookies(self):
        if os.path.isfile(self._cookie_file) and \
                os.stat(self._cookie_file).st_size > 0:
            with open(self._cookie_file, 'rb') as fd:
                self._session.cookies.update(pickle.load(fd))
            self._log.info('Cookies from %s loaded', self._cookie_file)
            return True
        return False

    def _purge_cookies(self):
        self._log.info('Purging cookies')
        with open(self._cookie_file, 'w'):
            pass

    def _save_cookies(self):
        with open(self._cookie_file, 'wb') as fd:
            pickle.dump(self._session.cookies, fd)
        self._log.info('Cookies saved to %s', self._cookie_file)

    def _validate_cookies(self, cookies):
        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)
        text = self._api._request(const.HZ_URL.format(url=const.BASE_URL)).text
        return not self._parser.is_prelogin(text)

    def _prepare_cookies(self):
        cookies = self._get_cookies()
        if self._validate_cookies(cookies):
            self._save_cookies()
        else:
            # TODO: raise something
            pass

    def _get_cookies(self):
        preload_page = self._api._request(const.BASE_URL).text
        js_aes_slow = self._api._request(const.COOKIES_JS_URL).text

        js_funcs, cookies = self._parser.parse_cookies(preload_page)
        value = js2py.eval_js('\n'.join([js_aes_slow, js_funcs]))
        cookies[const.COOKIES_JS_NAME] = value
        return cookies


class ZoneHAPI(metaclass=SingletonMeta):

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(const.HEADERS)
        self._cookies = Cookies(self, self._session)
        self._random_ua = _CONF['zoneh']['random_ua']
        self._parser = HTMLParser()
        self._log = logging.getLogger(self.__class__.__name__)

    def init_cookies(self, force=False):
        self._cookies.init_cookies(force=force)

    def get_page(self, page_num, type_):
        page_url = const.ARCHIVE_TYPES[type_]['page']
        return self._request(page_url.format(page_num=page_num)).text

    def get_mirror_page(self, mirror_id):
        return self._request(const.MIRROR_URL.format(mirror_id=mirror_id)).text

    def get_captcha_img(self):
        url = const.CAPTCHA_URL.format(captcha_num=get_captcha_number())
        return BytesIO(self._request(url).content)

    def solve_captcha(self, text, page):
        self._log.info('Solving captcha with text "%s", page %s', text, page)
        self._log.debug('Cookies: %s', self._session.cookies.get_dict())
        url = const.ARCHIVE_TYPES[page[0]]['page'].format(page_num=page[1])
        res = self._request(method='POST', url=url, data={'captcha': text})
        return not self._parser.is_captcha(res.content)

    def _request(self, url, method='GET', data=None):
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
        return result

    def _update_headers(self):
        if self._random_ua:
            headers = const.HEADERS
            headers['User-Agent'] = get_randoma_ua()
            self._log.debug('Random UA: %s', headers['User-Agent'])
            self._session.headers.update(headers)
