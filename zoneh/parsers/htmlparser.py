"""HTML parser module."""

import logging
import re
from collections import OrderedDict

from bs4 import BeautifulSoup

from zoneh.const import (
    CAPTCHA_ID, COOKIES_JS_REGEX, MIRROR_LI_CLASS, MIRROR_PAGE_MAP,
    PRELOGIN_CONDITION, TBL_ID, TBL_MAP, TBL_PAGE_NUMS_ROW_ID, TBL_SKIP_ROWS
)
from zoneh.decorators import content_handler
from zoneh.utils import Singleton


class HtmlSoup(BeautifulSoup):
    def __init__(self, page):
        """Class constructor."""
        super().__init__(page, 'html.parser')


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
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self._soup = HtmlSoup(page)
        self._elems = self._soup.find_all('li', {'class': MIRROR_LI_CLASS})

    def get_mirror_data(self):
        data = {}
        inner_1 = self._elems[MIRROR_PAGE_MAP['metadata_1']['index']]
        inner_2 = self._elems[MIRROR_PAGE_MAP['metadata_2']['index']]

        data['date'] = self._get_date()
        data['notifier'] = self._get_notifier(inner_1)
        data['defaced_url_full'] = self._get_url(inner_1)
        data['ip'], data['country'] = self._get_ip_and_country(inner_1)
        data['os'] = self._get_os(inner_2)
        data['server'] = self._get_server(inner_2)
        return data

    def _get_date(self):
        text = self._elems[MIRROR_PAGE_MAP['date']['index']].text
        return text.split(' ', 3)[-1]

    @staticmethod
    def _get_notifier(inner):
        _class = MIRROR_PAGE_MAP['metadata_1']['notifier']
        return inner.find('li', {'class': _class}).text.rsplit(' ', 1)[-1]

    @staticmethod
    def _get_url(inner):
        _class = MIRROR_PAGE_MAP['metadata_1']['defaced_url_full']
        return inner.find('li', {'class': _class}).text.rsplit(' ')[-1]

    @staticmethod
    def _get_ip_and_country(inner):
        _class = MIRROR_PAGE_MAP['metadata_1']['ip_and_country']
        li = inner.find('li', {'class': _class})
        ip = li.text.rstrip().rsplit(' ', 1)[-1]
        country = li.img.get('title') if li.img else ''
        return ip, country

    @staticmethod
    def _get_os(inner):
        _class = MIRROR_PAGE_MAP['metadata_2']['os']
        return inner.find('li', {'class': _class}).text.split(' ')[-1]

    @staticmethod
    def _get_server(inner):
        _class = MIRROR_PAGE_MAP['metadata_2']['server']
        return inner.find('li', {'class': _class}).text.split(' ')[-1]


class HTMLParser(metaclass=Singleton):
    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self._rev_map = {v: getattr(ColumnParser, k) for k, v in
                         TBL_MAP.items()}

    @staticmethod
    def parse_cookies(page):
        cookies = {}
        soup = HtmlSoup(page)

        js_script = soup.find_all('script')[-1].string
        if not js_script:
            # TODO
            pass

        match = re.match(COOKIES_JS_REGEX, js_script, re.MULTILINE)
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
        soup = HtmlSoup(page)
        table = soup.find('table', attrs={'id': TBL_ID})
        next_page = self.get_next_page(table)
        rows = table.find_all('tr')
        start_slice, end_slice = TBL_SKIP_ROWS

        for row in rows[start_slice:end_slice]:
            record = OrderedDict()
            cols = row.find_all('td')
            for index, col in enumerate(cols):
                record[self._rev_map[index].__name__] = \
                    self._rev_map[index](col)
            yield record, next_page

    @staticmethod
    def get_advanced_data(page):
        return MirrorPageParser(page).get_mirror_data()

    @staticmethod
    def get_next_page(table):
        row = table.find_all('tr')[TBL_PAGE_NUMS_ROW_ID]
        col = row.find('td')
        next_page = col.find('strong').find_next_sibling('a')
        return int(next_page.text) if next_page else None

    def is_captcha(self, page):
        self._log.debug('Parsing page for captcha')
        # self._log.debug(page)
        page = HtmlSoup(page)
        return bool(page.find('img', attrs={'id': CAPTCHA_ID}))

    @staticmethod
    def is_prelogin(page):
        return PRELOGIN_CONDITION in page
