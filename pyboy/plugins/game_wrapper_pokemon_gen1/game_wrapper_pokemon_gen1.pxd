#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
from pyboy.plugins.game_wrapper_pokemon_gen1.core.mem_manager cimport MemoryManager
cimport cython

cdef class GameWrapperPokemonGen1(PyBoyGameWrapper):
    cdef MemoryManager mem_manager