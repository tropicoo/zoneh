"""CSV processor module."""

import csv
import io
import logging


class CsvProcessor:

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)
        self._csv_fd = io.StringIO()

    def write(self, record):
        headers = []
        writer = None

        if not headers:
            headers = list(record.keys())
            writer = csv.DictWriter(self._csv_fd, fieldnames=headers,
                                    dialect='excel')
            writer.writeheader()
        writer.writerow(record)

    def get_data(self):
        try:
            return io.BytesIO(self._csv_fd.getvalue().encode('utf-8'))
        finally:
            self._clear()

    def _clear(self):
        self._csv_fd = io.StringIO()
