#!/usr/bin/env python3
"""Main entry point."""

from zoneh.launcher import ZBotLauncher
from zoneh.log import init_logging

__version__ = '0.2.2'


def main():
    """Main function."""
    init_logging()

    zoneh = ZBotLauncher()
    zoneh.run()


if __name__ == '__main__':
    main()
