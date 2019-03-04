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

cdef short testFlag(self, int flag)
cdef void setFlag(self, int flag, bint value=*)
cdef void clearFlag(self, int flag)

# ### Interrupt flags

cdef bint testInterruptFlag(self, int flag)
cdef void setInterruptFlag(self, int flag)
cdef void clearInterruptFlag(self, int flag)

cdef bint testInterruptFlagEnabled(self, int flag)

cdef bint testRAMRegisterFlag(self, int address, int flag)
cdef void setRAMRegisterFlag(self, int address, int flag, bint value=*)
cdef void clearRAMRegisterFlag(self, int address, int flag)
cdef bint testRAMRegisterFlagEnabled(self, int address, int flag)

