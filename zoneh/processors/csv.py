"""CSV processor module."""

import csv
import io
import logging


class CsvProcessor:
    """CSV data processor class."""

    def __init__(self):
        """Class constructor."""
        self._log = logging.getLogger(self.__class__.__name__)
        self._csv_fd = io.StringIO()

    def write(self, record):
        """Write record to CSV object."""
        headers = []
        writer = None

        if not headers:
            headers = list(record.keys())
            writer = csv.DictWriter(self._csv_fd, fieldnames=headers,
                                    dialect='excel')
            writer.writeheader()
        writer.writerow(record)

    def get_data(self):
        """Get CSV data."""
        try:
            return io.BytesIO(self._csv_fd.getvalue().encode('utf-8'))
        finally:
            self._clear()

    def _clear(self):
        """Clear existing CSV file descriptor."""
        self._csv_fd = io.StringIO()
