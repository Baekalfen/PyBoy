cimport cython


cdef int CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG

cdef class Logger:
  cdef str name

  cpdef void critical(self, str, ...) noexcept with gil
  cpdef void error(self, str, ...) noexcept with gil
  cpdef void warning(self, str, ...) noexcept with gil
  cpdef void info(self, str, ...) noexcept with gil
  cpdef void debug(self, str, ...) noexcept with gil