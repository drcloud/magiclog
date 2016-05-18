from collections import namedtuple
import inspect
import logging
import logging.handlers
import __main__
import os
import sys
import textwrap
from types import MethodType, ModuleType

from stackclimber import stackclimber


try:
    basestring
except NameError:
    basestring = str


def logger(ref=0):
    """Finds a module logger.

    If the argument passed is a module, find the logger for that module using
    the modules' name; if it's a string, finds a logger of that name; if an
    integer, walks the stack to the module at that height.

    The returned is always extended with a ``.configure()`` method allowing
    its log levels for syslog and stderr to be adjusted or automatically
    initialized as per the documentation for `configure()` below.
    """
    if inspect.ismodule(ref):
        return extend(logging.getLogger(ref.__name__))
    if isinstance(ref, basestring):
        return extend(logging.getLogger(ref))
    return extend(logging.getLogger(stackclimber(ref+1)))


def configure(logger=None, **kwargs):
    """Configures a logger, according to the following rules:

    * With no options set, enables ``INFO`` level on stderr if stderr is a TTY;
      otherwise enables ``INFO`` level to Syslog.

    * With ``syslog=`` and/or ``stderr=``, configures as specified.

    * With ``level=``, enables either Syslog or stderr logging according to
      whether or not stderr is a TTY, but uses the level specified.
    """
    configuration = Configuration.auto(**kwargs)
    if logger is None:
        logger = logging.getLogger()
    configuration(logger)


class Configuration(namedtuple('Configuration', 'syslog stderr extended')):
    def __call__(self, logger):
        log.info('Applying config %s to logger: %s', self, logger.name)
        if isinstance(logger, basestring):
            logger = logging.getLogger(logger)
        syslog, stderr = norm_level(self.syslog), norm_level(self.stderr)
        configure_handlers(logger, syslog=syslog, stderr=stderr,
                           extended=self.extended)
        set_normed_level(logger, min(_ for _ in [syslog, stderr] if _))

    @classmethod
    def auto(cls, syslog=None, stderr=None, level=None, extended=None):
        """Tries to guess a sound logging configuration.
        """
        level = norm_level(level)
        if syslog is None and stderr is None:
            if sys.stderr.isatty() or syslog_path() is None:
                log.info('Defaulting to STDERR logging.')
                syslog, stderr = None, (level or logging.INFO)
                if extended is None:
                    extended = (stderr or 0) <= logging.DEBUG
            else:
                log.info('Defaulting to logging with Syslog.')
                syslog, stderr = (level or logging.WARNING), None
        return cls(syslog=syslog, stderr=stderr, extended=extended)


def configure_handlers(logger, syslog=None, stderr=None, extended=False):
    stderr_handler, syslog_handler = None, None
    if stderr is not None:
        stderr_handler = logging.StreamHandler()
        configure_stderr_format(stderr_handler, extended)
        if stderr != logging.NOTSET:
            stderr_handler.level = stderr
    if syslog is not None:
        dev = syslog_path()
        cmd = os.path.basename(sys.argv[0])
        app = __main__.__name__
        app = cmd if app in ['__main__'] else app
        fmt = app + '[%(process)d]: %(name)s %(funcName)s %(message)s'
        syslog_handler = logging.handlers.SysLogHandler(address=dev)
        syslog_handler.setFormatter(logging.Formatter(fmt=fmt))
        if syslog != logging.NOTSET:
            syslog_handler.level = syslog
    clear_handlers(logger)
    logger.handlers = [h for h in [stderr_handler, syslog_handler] if h]


syslog_paths = ['/dev/log', '/var/run/syslog']


def syslog_path():
    for path in syslog_paths:
        if os.path.exists(path):
            return path


def set_normed_level(logger, level):
    level = norm_level(level)
    if level is not None:
        logger.level = level


def configure_stderr_format(stderr_handler, extended=False):
    if extended:
        fmt = Formatter(datefmt='%H:%M:%S')
    else:
        fmt = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(message)s',
                                datefmt='%H:%M:%S')
    stderr_handler.setFormatter(fmt)


def extend(logger):
    logger.configure = MethodType(configure, logger)
    logger.handlers += [_null_handler]
    return logger


try:
    _levels = dict((k.lower(), v) for k, v in logging._levelNames.items()
                   if isinstance(k, basestring))
except AttributeError:
    _levels = dict((k.lower(), v) for k, v in logging._nameToLevel.items()
                   if isinstance(k, basestring))


def norm_level(level):
    if level is None:
        return level
    if isinstance(level, basestring):
        return _levels[level.lower()]
    else:
        assert level in _levels.values()
        return level


def levels():
    return set(_levels.keys())


def clear_handlers(root_of_loggers):
    loggers = [root_of_loggers]
    if isinstance(root_of_loggers, logging.RootLogger):
        loggers = logging.Logger.manager.loggerDict.values()
    else:
        for name, logger in logging.Logger.manager.loggerDict.items():
            if name.startswith(root_of_loggers.name + '.'):
                loggers += [logger]
    for logger in loggers:
        logger.handlers = []


try:
    _null_handler = logging.NullHandler()
except:
    # Python 2.6 compatibility
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    _null_handler = NullHandler()


class Formatter(logging.Formatter):
    wrapper = textwrap.TextWrapper(drop_whitespace=True,
                                   initial_indent='  ',
                                   subsequent_indent='  ',
                                   break_long_words=False,
                                   break_on_hyphens=False,
                                   width=76)

    def format(self, rec):
        """
        :type rec: logging.LogRecord
        """
        t = self.formatTime(rec, self.datefmt)
        func = '' if rec.funcName == '<module>' else ' %s()' % rec.funcName
        left_header_data = (t, rec.msecs, rec.name, func, rec.lineno)
        left_header = '%s.%03d %s%s @ %d' % left_header_data
        right_header = rec.levelname.lower()
        spacer = 79 - 4 - len(left_header) - len(right_header)
        top_line = left_header + ' -' + spacer * '-' + '- ' + right_header
        lines = [_ for __ in textwrap.dedent(rec.getMessage()).splitlines()
                 for _ in self.wrapper.wrap(__)]

        # This is more or less the logic in logging.Formatter.format() for
        # exception logging, though greatly condensed.
        if rec.exc_info:
            exc_text = super(Formatter, self).formatException(rec.exc_info)
            exc_lines = exc_text.splitlines()
            # if len(exc_lines) > 4:
            #     exc_lines = exc_lines[:2] + ['...'] + exc_lines[-2:]
            lines += [''] + ['  ' + l for l in exc_lines]

        return top_line + '\n' + '\n'.join(l for l in lines)


# This is how we overload `import`. Modelled on Andrew Moffat's `sh`.
class ImportWrapper(ModuleType):
    def __init__(self, module):
        self._module = module

        # From the original -- these attributes are special.
        for attr in ['__builtins__', '__doc__', '__name__', '__package__']:
            setattr(self, attr, getattr(module, attr, None))

        # Path settings per original -- seemingly obligatory.
        self.__path__ = []

    def __getattr__(self, name):
        if name == 'log':
            return logger(1)
        return getattr(self._module, name)


log = logger(__name__)


self = sys.modules[__name__]
sys.modules[__name__] = ImportWrapper(self)
