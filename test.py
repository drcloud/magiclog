import logging

from magiclog import log


def test_logger_name():
    # Because this file is called ``test.py`` and not a real module, the
    # logger should be named ``test``.
    assert log.name == 'test'


def test_logger_level():
    # Without a level set for both syslog and non, level must be the lowest
    # possible.
    assert log.level == logging.NOTSET


def test_logger_not_crashing():
    log.configure()
    log.info('Hello Info.')
