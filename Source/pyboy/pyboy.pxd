#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from libc cimport time
cimport cython

from pyboy.motherboard.motherboard cimport Motherboard
from pyboy.window.window cimport Window


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef float SPF

cdef class PyBoy:
    cdef object debugger
    cdef unicode ROM
    cdef Motherboard motherboard
    cdef Window window

    cdef bint profiling
    cdef double avg_emu
    cdef double avg_cpu
    cdef unsigned int counter
    cdef bint limit_emulationspeed
    cdef int emulationspeed, max_emulationspeed
    cdef object screen_recorder

    @cython.locals(done=cython.bint, event=int, t_start=float, t_cpu=float, t_emu=float, secs=float)
    cpdef bint tick(self)
    cpdef void stop(self, save=*)


#    ###########################
#    #
#    # Scripts and bot methods
#    cpdef object getScreenBuffer(self)
#    cpdef unsigned char getMemoryValue(self, unsigned short)
#    cpdef void setMemoryValue(self, unsigned short, unsigned char)
#    cpdef void sendInput(self, unsigned int)
#    cpdef object getMotherBoard(self)
#    cpdef object getSprite(self, unsigned int)
#    cpdef object getTileView(self, bint)
#    cpdef tuple getScreenPosition(self)
