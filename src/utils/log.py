import os
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler


FMT = '[%(asctime)s]-[%(name)s]-[%(filename)s:%(lineno)d]-[%(process)d:%(thread)d]-[%(levelname)s]:%(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'


def _get_level(env=None):

    if env is None:
        env = os.environ.get('RUN_MODE', 'development')

    if env == 'development':
        level = logging.DEBUG
    elif env == 'test':
        level = logging.INFO
    elif env == 'production':
        level = logging.INFO
    else:
        level = logging.ERROR

    return level


def _get_handler_console(fmt, datefmt, level):

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt, datefmt))
    handler.setLevel(level)
    return handler


def _get_handler_rotating_file(filepath, fmt, datefmt, level):
    handler = TimedRotatingFileHandler(filename=filepath,
                                       when="midnight",
                                       backupCount=15,
                                       encoding='utf-8')
    handler.setFormatter(logging.Formatter(fmt, datefmt))
    handler.setLevel(level)
    return handler


def _get_handler_file(filepath, fmt, datefmt, level):
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(logging.Formatter(fmt, datefmt))
    handler.setLevel(level)
    return handler


def get_file_logger(filepath=None,
                    name=None,
                    is_timerotate=False,
                    level=None,
                    fmt=None,
                    datefmt=None):
    """"""

    logger = logging.getLogger(name) if isinstance(name, str) else logging.getLogger()

    fmt = fmt if fmt else FMT
    datefmt = datefmt if datefmt else DATEFMT
    level = level if level in [10, 20, 30, 40, 50] else _get_level()

    # handler
    if not logger.hasHandlers():
        if is_timerotate:
            handler = _get_handler_rotating_file(filepath, fmt, datefmt, level,)
        else:
            handler = _get_handler_file(filepath, fmt, datefmt, level,)
        logger.addHandler(handler)

        logger.setLevel(level)

        handler.close()

    return logger


def get_console_logger(name=None,
                       propagate=False,
                       level=None,
                       fmt=None,
                       datefmt=None,
                       ):
    logger = logging.getLogger(name) if isinstance(name, str) else logging.getLogger()

    fmt = fmt if fmt else FMT
    datefmt = datefmt if datefmt else DATEFMT
    level = level if level in [10, 20, 30, 40, 50] else _get_level()

    logger.propagate = propagate
    logger.setLevel(level)

    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(fmt, datefmt))
        ch.setLevel(level)
        logger.addHandler(ch)
        ch.close()

    return logger


general_logger = get_console_logger('GEN')
