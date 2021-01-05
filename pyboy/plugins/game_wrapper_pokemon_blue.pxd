from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

# Fun fact: I'm not familiar with Cython. I dont know why this lib is obsessed with it
# When in doubt if I can't expose the variable I can always put it in a function...
cdef int ROWS, COLS

cdef class Fitness:
    cdef public GameWrapperPokemonBlue game_wrapper

cdef class GameWrapperPokemonBlue(PyBoyGameWrapper):
    cdef public int fitness
    cdef public Fitness fitness_impl

cdef class RandomizeOnReset(Fitness):
    cdef public list fitness_impls
    cdef public int current_fitness_impl

cdef class Strict(Fitness):
    pass

cdef class OptimalOptions(Fitness):
    pass

cdef class FindAllMaps(Fitness):
    cdef public dict map_cache

