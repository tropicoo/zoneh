"""FormattedRecord module."""

import inspect

from zoneh.const import MIRROR_URL, MASS_DEFACEMENT_URL, REDEFACEMENT_URL
from zoneh.utils import get_func_name


class Record:
    """Represent Zone-H table record."""

    def __init__(self, record):
        """Class constructor.

        Represent Zone-H table row as record object.
        """
        self._record = record

    def __repr__(self):
        return f'<Record {self._record}>'

    def __getitem__(self, index):
        return self._record[index]

    @property
    def date(self):
        return self._record[get_func_name()]

    @property
    def notifier(self):
        return self._record[get_func_name()]

    @property
    def homepage_defacement(self):
        return self._record[get_func_name()]

    @property
    def mass_defacement(self):
        ipaddr = self._record[get_func_name()]
        return MASS_DEFACEMENT_URL.format(ip=ipaddr) if ipaddr else 'False'

    @property
    def redefacement(self):
        domain = self._record[get_func_name()]
        return REDEFACEMENT_URL.format(domain=domain) if domain else 'False'

    @property
    def country(self):
        return self._record[get_func_name()]

    @property
    def special(self):
        return self._record[get_func_name()]

    @property
    def defaced_url(self):
        return self._record[get_func_name()]

    @property
    def os(self):
        return self._record[get_func_name()]

    @property
    def mirror(self):
        mirror_id = self._record[get_func_name()]
        return MIRROR_URL.format(mirror_id=mirror_id)


class FormattedRecord(Record):
    def __init__(self, record, rec_num=None):
        """Class constructor."""
        super().__init__(record)
        self._rec_num = rec_num
        self.data = self.format()

    def __str__(self):
        return self.format()

    def __repr__(self):
        return self.__str__()

    def format(self):
        """Format record object."""
        message = f"""<pre>Record #{self._rec_num}
                      Date: {self.date}
                      Notifier: {self.notifier}
                      Homepage Defacement: {self.homepage_defacement}
                      Mass Defacement: {self.mass_defacement}
                      Redefacement: {self.redefacement}
                      Country: {self.country}
                      Special: {self.special}
                      URL: {self.defaced_url}
                      OS: {self.os}
                      Mirror: {self.mirror}
                      </pre>"""
        return inspect.cleandoc(message)
