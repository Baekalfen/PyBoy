#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from libc.stdint cimport uint8_t

from pyboy.plugins.base_plugin cimport PyBoyPlugin


cdef int PRINTER_INIT, PRINTER_PRINT, PRINTER_DATA, PRINTER_STATUS
cdef int MAGIC1, MAGIC2, COMMAND, COMPRESSION, LENGTH_LSB, LENGTH_MSB
cdef int DATA, CHECKSUM_LSB, CHECKSUM_MSB, ALIVE, STATUS
cdef int PRINTER_WIDTH, PRINTER_MAX_HEIGHT, PRINTER_BUFFER_SIZE, PRINTER_MAX_DATA


cdef class GameBoyPrinter(PyBoyPlugin):
    cdef public object output_dir
    cdef public bint _enabled

    cdef public uint8_t command_state
    cdef public uint8_t command_id
    cdef public uint8_t compression
    cdef public int length_left
    cdef public int command_length
    cdef public int checksum
    cdef public uint8_t status
    cdef public uint8_t byte_to_send

    cdef public array command_data
    cdef public array image
    cdef public int image_offset

    cdef public int compression_run_length
    cdef public bint compression_run_is_compressed

    cdef public uint8_t print_margins
    cdef public uint8_t print_palette
    cdef public uint8_t print_exposure

    cdef public object _stitch_image
    cdef public int _print_count
    cdef public int time_remaining
    cdef public object _last_image

    cdef void _initialize(self) noexcept
    cpdef void process_byte(self, uint8_t) except *
    cdef void _decompress_byte(self, uint8_t) noexcept
    cdef void _handle_command(self) except *
    cdef void _decode_and_save_image(self) except *
    cdef void _flush_stitch(self) except *
    cdef void tick(self, int) noexcept
    cpdef object get_image(self)
    cpdef void stop(self) except *
