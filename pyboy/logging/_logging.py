from . import CRITICAL, DEBUG, ERROR, INFO, WARNING, _log


class Logger:
    def __init__(self, name):
        self.name = name

    def critical(self, fmt, *args):
        _log(self.name, "CRITICAL", CRITICAL, fmt, args)

    def error(self, fmt, *args):
        _log(self.name, "ERROR", ERROR, fmt, args)

    def warning(self, fmt, *args):
        _log(self.name, "WARNING", WARNING, fmt, args)

    def info(self, fmt, *args):
        _log(self.name, "INFO", INFO, fmt, args)

    def debug(self, fmt, *args):
        _log(self.name, "DEBUG", DEBUG, fmt, args)
