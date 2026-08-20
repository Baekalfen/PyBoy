#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyPlugin


cdef Logger logger

cdef class GdbServer(PyBoyPlugin):
    cdef object sock
    cdef object client_socket
    cdef object client_address
    cdef object buffer
    cdef bint freeze