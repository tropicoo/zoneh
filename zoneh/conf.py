"""Config module."""

import json
import logging
import os

from zoneh.exceptions import ConfigError

_LOG = logging.getLogger(__name__)
_CONFIG_FILE = 'config.json'


def _load_config():
    """Load telegram and filters configuration from config file."""
    if not os.path.isfile(_CONFIG_FILE):
        err_msg = 'Can\'t find {0} configuration file'.format(_CONFIG_FILE)
        _LOG.error(err_msg)
        raise ConfigError(err_msg)

    with open(_CONFIG_FILE, 'r') as fd:
        config = fd.read()
    try:
        config = json.loads(config)
    except json.decoder.JSONDecodeError:
        err_msg = 'Malformed JSON in {0} ' \
                  'configuration file'.format(_CONFIG_FILE)
        _LOG.error(err_msg)
        raise ConfigError(err_msg)
    return config


_CONF = _load_config()


def get_config():
    return _CONF
