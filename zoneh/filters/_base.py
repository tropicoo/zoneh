import logging


class BaseFilter:
    TYPE = None

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f'<{self.__class__.__name__} type:{self.TYPE}>'

    def match(self, record):
        raise NotImplementedError
