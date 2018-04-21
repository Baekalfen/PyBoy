# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef class RTC:
    cdef bint latchEnabled
    cdef double timeZero
    cdef unsigned int secLatch
    cdef unsigned int minLatch
    cdef unsigned int hourLatch
    cdef unsigned int dayLatchLow
    cdef unsigned int dayLatchHigh
    cdef unsigned int dayCarry
    cdef unsigned int halt

    cdef void save(self, unicode)
    cdef void load(self, unicode)
    cdef void latchRTC(self)
    cdef void writeCommand(self, unsigned char)
    cdef unsigned char getRegister(self, unsigned char)
    cdef void setRegister(self, unsigned char, unsigned char)

