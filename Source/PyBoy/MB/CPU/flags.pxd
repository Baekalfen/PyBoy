# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

### CPU Flags
# cdef extern short flagC, flagH, flagN, flagZ
# cdef extern short VBlank, LCDC, TIMER, Serial, HightoLow
# cdef short flagC, flagH, flagN, flagZ
# cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cpdef short testFlag(self, int flag)
cpdef void setFlag(self, int flag, bint value=*)
cpdef void clearFlag(self, int flag)

# ### Interrupt flags

cpdef bint testInterruptFlag(self, int flag)
cpdef void setInterruptFlag(self, int flag)
cpdef void clearInterruptFlag(self, int flag)

cpdef bint testInterruptFlagEnabled(self, int flag)

cpdef bint testRAMRegisterFlag(self, int address, int flag)
cpdef void setRAMRegisterFlag(self, int address, int flag, bint value=*)
cpdef void clearRAMRegisterFlag(self, int address, int flag)
cpdef bint testRAMRegisterFlagEnabled(self, int address, int flag)

