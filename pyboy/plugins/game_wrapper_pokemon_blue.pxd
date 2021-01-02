from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

cdef int ROWS, COLS


cdef class GameWrapperPokemonBlue(PyBoyGameWrapper):
    cdef public int fitness