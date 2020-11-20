import logging


def init_logging():
    log_format = '%(asctime)s - [%(levelname)s] - [%(name)s:%(lineno)d] - %(message)s'
    logging.basicConfig(format=log_format)
