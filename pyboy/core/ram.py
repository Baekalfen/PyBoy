#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array

# MEMORY SIZES
INTERNAL_RAM0 = 8 * 1024 # 8KB
NON_IO_INTERNAL_RAM0 = 0x60
IO_PORTS = 0x4C
NON_IO_INTERNAL_RAM1 = 0x34
INTERNAL_RAM1 = 0x7F
INTERRUPT_ENABLE_REGISTER = 1


class RAM:
    def __init__(self, random=False):
        if random: # NOTE: In real life, the RAM is scrambled with random data on boot.
            raise Exception("Random RAM not implemented")

        self.internal_ram0 = array.array("B", [0] * (INTERNAL_RAM0))
        self.non_io_internal_ram0 = array.array("B", [0] * (NON_IO_INTERNAL_RAM0))
        self.io_ports = array.array("B", [0] * (IO_PORTS))
        self.internal_ram1 = array.array("B", [0] * (INTERNAL_RAM1))
        self.non_io_internal_ram1 = array.array("B", [0] * (NON_IO_INTERNAL_RAM1))
        self.interrupt_register = array.array("B", [0] * (INTERRUPT_ENABLE_REGISTER))

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
