import re

from . import CRITICAL, DEBUG, ERROR, INFO, WARNING, _log, get_log_level

cimport cython
from cpython cimport PyObject, PyObject_Str
from libc.stdio cimport FILE, fprintf, stderr, stdout
from libc.stdlib cimport free, malloc
from libc.string cimport strchr, strcpy


cdef extern from "stdarg.h":
    ctypedef struct va_list:
        pass
    ctypedef struct fake_type:
        pass
    void va_start(va_list, void* arg) noexcept nogil
    void* va_arg(va_list, fake_type) noexcept nogil
    void va_end(va_list) noexcept nogil
    fake_type int_type "int"
    fake_type pyobject_type "PyObject*"
    fake_type double_type "double"

cdef extern from "stdio.h":
    cdef int vfprintf(FILE *stream, const char* format, va_list arg) noexcept nogil


cdef list get_params(str fmt):
    cdef list params = []
    for idx, p in [(m.start(), m.groups()[0]) for m in re.finditer('%[0-9\.]*([xdsf])', fmt)]:
        params.append(p)
    return params

cdef list get_args(va_list ap, str fmt):
    cdef list args = []
    for p in get_params(fmt):
        if p in ['d', 'x']:
            args.append(<int> va_arg(ap, int_type))
        elif p == 'f':
            args.append(<double> va_arg(ap, double_type))
        elif p == 's':
            args.append(PyObject_Str(<object>(<PyObject*> va_arg(ap, pyobject_type))))
        else:
            val = -1
            args.append(0)
    return args

cdef class Logger:
    def __init__(self, str name):
        self.name = name

    cpdef void critical(self, str fmt, ...) noexcept with gil:
        if get_log_level() > CRITICAL:
            return

        cdef va_list ap
        va_start(ap, <void*>fmt)
        cdef list args = get_args(ap, fmt)
        va_end(ap)

        _log(self.name, "CRITICAL", CRITICAL, fmt, args)

    cpdef void error(self, str fmt, ...) noexcept with gil:
        if get_log_level() > ERROR:
            return

        cdef va_list ap
        va_start(ap, <void*>fmt)
        cdef list args = get_args(ap, fmt)
        va_end(ap)

        _log(self.name, "ERROR", ERROR, fmt, args)

    cpdef void warning(self, str fmt, ...) noexcept with gil:
        if get_log_level() > WARNING:
            return

        cdef va_list ap
        va_start(ap, <void*>fmt)
        cdef list args = get_args(ap, fmt)
        va_end(ap)

        _log(self.name, "WARNING", WARNING, fmt, args)

    cpdef void info(self, str fmt, ...) noexcept with gil:
        if get_log_level() > INFO:
            return

        cdef va_list ap
        va_start(ap, <void*>fmt)
        cdef list args = get_args(ap, fmt)
        va_end(ap)

        _log(self.name, "INFO", INFO, fmt, args)

    cpdef void debug(self, str fmt, ...) noexcept with gil:
        if get_log_level() > DEBUG:
            return

        cdef va_list ap
        va_start(ap, <void*>fmt)
        cdef list args = get_args(ap, fmt)
        va_end(ap)

        _log(self.name, "DEBUG", DEBUG, fmt, args)

