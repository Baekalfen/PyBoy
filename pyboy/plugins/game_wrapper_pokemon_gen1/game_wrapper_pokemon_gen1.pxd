#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
from pyboy.plugins.game_wrapper_pokemon_gen1.core.gen_1_memory_manager cimport Gen1MemoryManager
cimport cython

cdef class GameWrapperPokemonGen1(PyBoyGameWrapper):
    cdef Gen1MemoryManager memory_manager