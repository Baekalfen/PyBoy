#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array
from random import getrandbits

# MEMORY SIZES
INTERNAL_RAM0 = 8 * 1024 # 8KiB
NON_IO_INTERNAL_RAM0 = 0x60
IO_PORTS = 0x4C
NON_IO_INTERNAL_RAM1 = 0x34
INTERNAL_RAM1 = 0x7F
INTERRUPT_ENABLE_REGISTER = 1


class RAM:
    def __init__(self, randomize=False):
        self.internal_ram0 = array("B", [0] * (INTERNAL_RAM0))
        self.non_io_internal_ram0 = array("B", [0] * (NON_IO_INTERNAL_RAM0))
        self.io_ports = array("B", [0] * (IO_PORTS))
        self.internal_ram1 = array("B", [0] * (INTERNAL_RAM1))
        self.non_io_internal_ram1 = array("B", [0] * (NON_IO_INTERNAL_RAM1))
        self.interrupt_register = array("B", [0] * (INTERRUPT_ENABLE_REGISTER))

        if randomize:
            for i in range(INTERNAL_RAM0):
                self.internal_ram0[i] = getrandbits(8)
            for i in range(NON_IO_INTERNAL_RAM0):
                self.non_io_internal_ram0[i] = getrandbits(8)
            for i in range(INTERNAL_RAM1):
                self.internal_ram1[i] = getrandbits(8)
            for i in range(NON_IO_INTERNAL_RAM1):
                self.non_io_internal_ram1[i] = getrandbits(8)

    def save_state(self, f):
        for n in range(INTERNAL_RAM0):
            f.write(self.internal_ram0[n])
        for n in range(NON_IO_INTERNAL_RAM0):
            f.write(self.non_io_internal_ram0[n])
        for n in range(IO_PORTS):
            f.write(self.io_ports[n])
        # TODO: Order of INTERNAL_RAM1 and NON_IO_INTERNAL_RAM1 is flipped
        for n in range(INTERNAL_RAM1):
            f.write(self.internal_ram1[n])
        for n in range(NON_IO_INTERNAL_RAM1):
            f.write(self.non_io_internal_ram1[n])
        for n in range(INTERRUPT_ENABLE_REGISTER):
            f.write(self.interrupt_register[n])

    def load_state(self, f, state_version):
        for n in range(INTERNAL_RAM0):
            self.internal_ram0[n] = f.read()
        for n in range(NON_IO_INTERNAL_RAM0):
            self.non_io_internal_ram0[n] = f.read()
        for n in range(IO_PORTS):
            self.io_ports[n] = f.read()
        # TODO: Order of INTERNAL_RAM1 and NON_IO_INTERNAL_RAM1 is flipped
        for n in range(INTERNAL_RAM1):
            self.internal_ram1[n] = f.read()
        for n in range(NON_IO_INTERNAL_RAM1):
            self.non_io_internal_ram1[n] = f.read()
        for n in range(INTERRUPT_ENABLE_REGISTER):
            self.interrupt_register[n] = f.read()
