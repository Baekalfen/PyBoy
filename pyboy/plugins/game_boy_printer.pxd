#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from libc.stdint cimport uint8_t

from pyboy.plugins.base_plugin cimport PyBoyPlugin


cdef int PRINTER_DATA, PRINTER_INIT, PRINTER_PRINT, PRINTER_STATUS
cdef int MAGIC1, MAGIC2, COMMAND, COMPRESSION, LENGTH_LSB, LENGTH_MSB
cdef int DATA, CHECKSUM_LSB, CHECKSUM_MSB, ALIVE, STATUS
cdef int PRINTER_WIDTH, PRINTER_MAX_HEIGHT, PRINTER_BUFFER_SIZE, PRINTER_MAX_DATA


cdef class GameBoyPrinter(PyBoyPlugin):
    cdef object output_dir
    cdef bint _enabled

    cdef uint8_t command_state
    cdef uint8_t command_id
    cdef uint8_t compression_enabled
    cdef int bytes_remaining
    cdef int data_length
    cdef int checksum
    cdef uint8_t status
    cdef uint8_t response_byte

    cdef array command_data
    cdef array image
    cdef uint8_t[:] command_data_view
    cdef uint8_t[:] image_view
    cdef int image_offset

    cdef int run_length
    cdef bint run_compressed

    cdef uint8_t print_margins
    cdef uint8_t print_palette
    cdef uint8_t print_exposure

    cdef object _stitch_image
    cdef int _print_count
    cdef int time_remaining
    cdef object _last_image
    cdef bint image_pending

    cdef void __set_mb_serial(self) except *
    cdef void _initialize(self) noexcept
    cdef void post_tick(self) noexcept
    cpdef void process_byte(self, uint8_t) except *
    cdef void process_byte_nogil(self, uint8_t) noexcept nogil
    cdef bint _consume_header(self, uint8_t) noexcept nogil
    cdef void _consume_data(self, uint8_t) noexcept nogil
    cdef bint _consume_checksum(self, uint8_t) noexcept nogil
    cdef void _consume_alive(self) noexcept nogil
    cdef void _decompress_byte(self, uint8_t) noexcept nogil
    cdef void _apply_command_nogil(self) noexcept nogil
    cdef void _flush_pending_image(self) except *
    cdef void _decode_image(self) except *
    cdef void _flush_stitch(self) except *
    cdef void tick(self, int) noexcept
    cpdef object get_image(self)
    cpdef void stop(self) except *
