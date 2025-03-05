(
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
) = range(5)

_log_level = WARNING


def get_log_level():
    return _log_level


def _log(name, pre_msg, level, fmt, args):
    # print(name, pre_msg, level, fmt, args)
    if get_log_level() > level:
        return
    if args:
        msg = fmt % tuple(args)
    else:
        msg = fmt
    print(name.ljust(30) + " " + pre_msg.ljust(8) + " " + msg)


try:
    from .logging import Logger
except ImportError:
    from ._logging import Logger


def log_level(level):
    global _log_level
    if level == "DEBUG":
        level = DEBUG
    elif level == "INFO":
        level = INFO
    elif level == "WARNING":
        level = WARNING
    elif level == "ERROR":
        level = ERROR
    elif level == "CRITICAL":
        level = CRITICAL
    elif level == "DISABLE":
        level = CRITICAL
    elif isinstance(level, int):
        pass
    else:
        raise ValueError(f"Invalid log level: {level}")

    _log_level = level


def get_logger(name):
    return Logger(name)
