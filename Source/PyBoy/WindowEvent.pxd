# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cdef QUIT 1

# cdef class WindowEvent:
# cpdef public unsigned int
cdef enum WindowEvent:
    Quit, PressArrowUp, PressArrowDown, PressArrowRight, PressArrowLeft, PressButtonA, PressButtonB, PressButtonSelect, PressButtonStart, ReleaseArrowUp, ReleaseArrowDown, ReleaseArrowRight, ReleaseArrowLeft, ReleaseButtonA, ReleaseButtonB, ReleaseButtonSelect, ReleaseButtonStart, DebugToggle, PressSpeedUp, ReleaseSpeedUp, SaveState, LoadState, Pass
