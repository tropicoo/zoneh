"""FormattedRecord module."""

import inspect

from zoneh.const import MIRROR_URL, MASS_DEFACEMENT_URL, REDEFACEMENT_URL
from zoneh.utils import get_func_name


class Record:
    def __init__(self, record):
        self._record = record

    def __repr__(self):
        return f'<Record {self._record}>'

    def __getitem__(self, index):
        return self._record[index]

    def date(self):
        return self._record[get_func_name()]

    def notifier(self):
        return self._record[get_func_name()]

    def homepage_defacement(self):
        return self._record[get_func_name()]

    def mass_defacement(self):
        ipaddr = self._record[get_func_name()]
        return MASS_DEFACEMENT_URL.format(ip=ipaddr) if ipaddr else 'False'

    def redefacement(self):
        domain = self._record[get_func_name()]
        return REDEFACEMENT_URL.format(domain=domain) if domain else 'False'

    def country(self):
        return self._record[get_func_name()]

    def special(self):
        return self._record[get_func_name()]

    def defaced_url(self):
        return self._record[get_func_name()]

    def os(self):
        return self._record[get_func_name()]

    def mirror(self):
        mirror_id = self._record[get_func_name()]
        return MIRROR_URL.format(mirror_id=mirror_id)


class FormattedRecord:
    def __init__(self, record, rec_num=None):
        self._rec = Record(record)
        self._rec_num = rec_num
        self.data = self.format()

    def __str__(self):
        return self.format()

    def __repr__(self):
        return self.__str__()

    def format(self):
        message = f"""<pre>Record #{self._rec_num}
                      Date: {self._rec.date()}
                      Notifier: {self._rec.notifier()}
                      Homepage Defacement: {self._rec.homepage_defacement()}
                      Mass Defacement: {self._rec.mass_defacement()}
                      Redefacement: {self._rec.redefacement()}
                      Country: {self._rec.country()}
                      Special: {self._rec.special()}
                      URL: {self._rec.defaced_url()}
                      OS: {self._rec.os()}
                      Mirror: {self._rec.mirror()}
                      </pre>"""
        return inspect.cleandoc(message)

    def get_mirror_url(self):
        return self._rec.mirror()
