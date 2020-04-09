"""Exceptions module."""


class ZoneHError(Exception):
    """Base ZoneH exception."""
    pass


class UserAuthError(ZoneHError):
    pass


class ConfigError(ZoneHError):
    pass


class ProcessorError(ZoneHError):
    pass


class PusherError(ZoneHError):
    pass


class ScraperError(ZoneHError):
    pass


class HTMLParserError(ZoneHError):
    pass


class HTMLParserCaptchaRequest(HTMLParserError):
    pass


class HTMLParserCookiesError(HTMLParserError):
    pass


class CaptchaError(ZoneHError):
    pass
