"""Config module."""

import json
import logging
import os

from zoneh.exceptions import ConfigError

_log = logging.getLogger(__name__)
_CONFIG_FILE = 'config.json'


def _load_config():
    """Load telegram and filters configuration from config file."""
    if not os.path.isfile(_CONFIG_FILE):
        err_msg = f'Cannot find {_CONFIG_FILE} configuration file'
        _log.error(err_msg)
        raise ConfigError(err_msg)

    with open(_CONFIG_FILE, 'r') as fd:
        config = fd.read()
    try:
        config = json.loads(config)
    except json.decoder.JSONDecodeError:
        err_msg = f'Malformed JSON in {_CONFIG_FILE} configuration file'
        _log.error(err_msg)
        raise ConfigError(err_msg)
    return config


_CONF = _load_config()


def get_config():
    return _CONF
