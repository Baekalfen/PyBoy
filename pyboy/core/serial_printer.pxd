#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t

from pyboy.core.serial cimport MAX_CYCLES, Serial
cimport pyboy.plugins.game_boy_printer


cdef class SerialPrinter(Serial):
    cdef pyboy.plugins.game_boy_printer.GameBoyPrinter printer
    cdef uint8_t _outgoing_byte
    cdef uint8_t _pending_response
