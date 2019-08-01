"""Constants module."""

import os
import sys

from zoneh.conf import get_config

_CONF = get_config()

LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

HOST = 'www.zone-h.org'
BASE_URL = f'https://{HOST}'

CAPTCHA_URL = f'{BASE_URL}/captcha.py?{{captcha_num}}'
CAPTCHA_ID = 'cryptogram'

_ARCHIVE_URL = f'{BASE_URL}/archive'
_ARCHIVE_PAGE_URL = f'{_ARCHIVE_URL}/page={{page_num}}'
_ARCHIVE_SPECIAL_URL = f'{_ARCHIVE_URL}/special=1'
_ARCHIVE_SPECIAL_PAGE_URL = f'{_ARCHIVE_SPECIAL_URL}/page={{page_num}}'
_ARCHIVE_ONHOLD_URL = f'{_ARCHIVE_URL}/published=0'
_ARCHIVE_ONHOLD_PAGE_URL = f'{_ARCHIVE_ONHOLD_URL}/published=0/page={{page_num}}'

ARCHIVE_TYPES = {
    'archive': {'base': _ARCHIVE_URL,
                'page': _ARCHIVE_PAGE_URL},
    'special': {'base': _ARCHIVE_SPECIAL_URL,
                'page': _ARCHIVE_SPECIAL_PAGE_URL},
    'onhold': {'base': _ARCHIVE_ONHOLD_URL,
               'page': _ARCHIVE_ONHOLD_PAGE_URL}}

MIRROR_URL = f'{BASE_URL}/mirror/id/{{mirror_id}}'
MASS_DEFACEMENT_URL = f'{_ARCHIVE_URL}/ip={{ip}}'
REDEFACEMENT_URL = f'{_ARCHIVE_URL}/domain={{domain}}'

TBL_ID = 'ldeface'
TBL_SKIP_ROWS = (1, -2)
TBL_PAGE_NUMS_ROW_ID = -2
TBL_MAP = {
    'date': 0,
    'notifier': 1,
    'homepage_defacement': 2,
    'mass_defacement': 3,
    'redefacement': 4,
    'country': 5,
    'special': 6,
    'defaced_url': 7,
    'os': 8,
    'mirror': 9,
}

MIRROR_LI_CLASS = 'deface0'
_M_DEFACEF = 'defacef'
_M_DEFACES = 'defaces'
_M_DEFACET = 'defacet'
MIRROR_PAGE_MAP = {
    'date': {'index': 0},
    'metadata_1': {'index': 1,
                   'notifier': _M_DEFACEF,
                   'defaced_url_full': _M_DEFACES,
                   'ip_and_country': _M_DEFACET},
    'metadata_2': {'index': 2,
                   'os': _M_DEFACEF,
                   'server': _M_DEFACES,
                   }}

START_PAGE = 1

HZ_URL = '{url}?hz=1'
COOKIES_JS_URL = f'{BASE_URL}/z.js'
COOKIES_JS_REGEX = r'(function.+(?=document)).+(toHex.+(?=\+)).+(expires.+?(?=;)).+(path=.+?(?=\"))'
COOKIES_JS_NAME = 'ZHE'
PRELOGIN_CONDITION = 'slowAES'

HEADERS = {'Host': HOST,
           'Connection': 'keep-alive',
           'Cache-Control': 'max-age=0',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.9'}

TMP_DIR = '{0}\\'.format(os.getenv('Temp')) \
    if sys.platform == 'win32' else '/tmp/'
