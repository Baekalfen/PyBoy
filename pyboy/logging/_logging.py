from . import CRITICAL, DEBUG, ERROR, INFO, WARNING, _log, get_log_level


class Logger:
    def __init__(self, name):
        self.name = name

    def critical(self, fmt, *args):
        _log(self.name, "_CRITICAL", CRITICAL, fmt, args)

    def error(self, fmt, *args):
        _log(self.name, "_ERROR", ERROR, fmt, args)

    def warning(self, fmt, *args):
        _log(self.name, "_WARNING", WARNING, fmt, args)

    def info(self, fmt, *args):
        _log(self.name, "_INFO", INFO, fmt, args)

    def debug(self, fmt, *args):
        _log(self.name, "_DEBUG", DEBUG, fmt, args)
