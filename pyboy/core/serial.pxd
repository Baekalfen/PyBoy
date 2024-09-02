# serial.pxd

cdef int INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW
cdef int SERIAL_FREQ, CPU_FREQ
cdef object async_recv

cdef class Serial:
    cdef object mb
    cdef int SC
    cdef int SB
    cdef object connection
    cdef int trans_bits
    cdef int cycles_count
    cdef int cycles_target
    cdef int serial_interrupt_based
    cdef object binding_connection
    cdef int is_master
    cdef bint transfer_enabled

    cpdef send_bit(self)
    cpdef bint recv_bit(self)
    cpdef bint tick(self)
    cpdef int cycles_to_transmit(self)
    cpdef stop(self)
