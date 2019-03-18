import logging
import re
from collections import OrderedDict
from functools import wraps

from bs4 import BeautifulSoup

import zoneh.const as const
import zoneh.exceptions
from zoneh.utils import is_generator

_LOG = logging.getLogger(__name__)


def _content_handler_helper(parser, page):
    if parser.is_captcha(page):
        err_msg = 'Captcha request'
        _LOG.error(err_msg)
        raise zoneh.exceptions.HTMLParserCaptchaRequest(err_msg)
    elif parser.is_prelogin(page):
        err_msg = 'Need to set cookies'
        _LOG.error(err_msg)
        raise zoneh.exceptions.HTMLParserCookiesError(err_msg)
    else:
        err_msg = 'Couldn\'t find HTML element. Check logs'
        _LOG.exception(err_msg)
        raise zoneh.exceptions.HTMLParserError(err_msg)


def content_handler(func):
    """HTML content handler decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        parser, page = args

        def iter_func():
            try:
                yield from func(*args, **kwargs)
            except Exception:
                _content_handler_helper(parser, page)
        try:
            return iter_func() if is_generator(func) else func(*args, **kwargs)
        except Exception:
            _content_handler_helper(parser, page)
    return wrapper


class Soup(BeautifulSoup):
    def __init__(self, page):
        super(Soup, self).__init__(page, 'html.parser')


class ColumnParser:
    @classmethod
    def date(cls, data):
        return data.text.strip()

    @classmethod
    def notifier(cls, data):
        return data.text.strip()

    @classmethod
    def homepage_defacement(cls, data):
        return bool(data.text.strip())

    @classmethod
    def mass_defacement(cls, data):
        return cls.__split_path(data)

    @classmethod
    def redefacement(cls, data):
        return cls.__split_path(data)

    @classmethod
    def country(cls, data):
        return data.find('img').get('title') if data.find('img') else ''

    @classmethod
    def special(cls, data):
        return bool(data.find('img'))

    @classmethod
    def defaced_url(cls, data):
        return data.text.strip()

    @classmethod
    def os(cls, data):
        return data.text.strip()

    @classmethod
    def mirror(cls, data):
        return int(data.find('a').get('href').rsplit('/', 1)[1])

    @classmethod
    def __split_path(cls, data):
        path = data.find('a')
        return path.get('href').split('=')[-1] if path else None


class MirrorPageParser:
    def __init__(self, page):
        self._soup = Soup(page)
        self._elems = self._soup.find_all('li', {'class': const.MIRROR_LI_CLASS})

    def get_mirror_data(self):
        data = {}
        inner_1 = self._elems[const.MIRROR_PAGE_MAP['metadata_1']['index']]
        inner_2 = self._elems[const.MIRROR_PAGE_MAP['metadata_2']['index']]

        data['date'] = self._get_date()
        data['notifier'] = self._get_notifier(inner_1)
        data['defaced_url_full'] = self._get_url(inner_1)
        data['ip'], data['country'] = self._get_ip_and_country(inner_1)
        data['os'] = self._get_os(inner_2)
        data['server'] = self._get_server(inner_2)
        return data

    def _get_date(self):
        text = self._elems[const.MIRROR_PAGE_MAP['date']['index']].text
        return text.split(' ', 3)[-1]

    def _get_notifier(self, inner):
        _class = const.MIRROR_PAGE_MAP['metadata_1']['notifier']
        return inner.find('li', {'class': _class}).text.rsplit(' ', 1)[-1]

    def _get_url(self, inner):
        _class = const.MIRROR_PAGE_MAP['metadata_1']['defaced_url_full']
        return inner.find('li', {'class': _class}).text.rsplit(' ')[-1]

    def _get_ip_and_country(self, inner):
        _class = const.MIRROR_PAGE_MAP['metadata_1']['ip_and_country']
        li = inner.find('li', {'class': _class})
        ip = li.text.rstrip().rsplit(' ', 1)[-1]
        country = li.img.get('title') if li.img else ''
        return ip, country

    def _get_os(self, inner):
        _class = const.MIRROR_PAGE_MAP['metadata_2']['os']
        return inner.find('li', {'class': _class}).text.split(' ')[-1]

    def _get_server(self, inner):
        _class = const.MIRROR_PAGE_MAP['metadata_2']['server']
        return inner.find('li', {'class': _class}).text.split(' ')[-1]


class HTMLParser:
    def __init__(self):
        self._rev_map = {v: getattr(ColumnParser, k) for k, v in const.TBL_MAP.items()}

    def parse_cookies(self, page):
        cookies = {}
        soup = Soup(page)

        js_script = soup.find_all('script')[-1].text
        if not js_script:
            # TODO
            pass

        match = re.match(const.COOKIES_JS_REGEX, js_script, re.MULTILINE)
        if not match:
            # TODO
            pass

        for group_id in range(3, 5):
            split = match.group(group_id).split('=')
            cookies[split[0]] = split[1]

        # Joined two js functions and two cookies dict: 'expires' and 'path'
        return '\n'.join([match.group(1), match.group(2)]), cookies

    @content_handler
    def get_records(self, page):
        soup = Soup(page)
        table = soup.find('table', attrs={'id': const.TBL_ID})
        next_page = self.get_next_page(table)
        rows = table.find_all('tr')
        start_slice, end_slice = const.TBL_SKIP_ROWS

        for row in rows[start_slice:end_slice]:
            record = OrderedDict()
            cols = row.find_all('td')
            for index, col in enumerate(cols):
                record[self._rev_map[index].__name__] = \
                    self._rev_map[index](col)
            yield record, next_page

    def get_advanced_data(self, page):
        return MirrorPageParser(page).get_mirror_data()

    def get_next_page(self, table):
        row = table.find_all('tr')[const.TBL_PAGE_NUMS_ROW_ID]
        col = row.find('td')
        next_page = col.find('strong').find_next_sibling('a')
        return int(next_page.text) if next_page else None

    def is_captcha(self, page):
        page = Soup(page)
        return bool(page.find('img', attrs={'id': const.CAPTCHA_ID}))

    def is_prelogin(self, page):
        return const.PRELOGIN_CONDITION in page
