#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.utils import MAX_CYCLES

# http://problemkaputt.de/pandocs.htm#gameboytechnicaldata Unless the
# oscillator frequency is multiplied or divided before it gets to the
# CPU, it must be running at 4.194304MHz (or if the CPU has an
# internal oscillator).
#
# http://problemkaputt.de/pandocs.htm#timeranddividerregisters
# Depending on the TAC register, the timer can run at one of four
# frequencies
# 00:   4096 Hz (OSC/1024)
# 01: 262144 Hz (OSC/16)
# 10:  65536 Hz (OSC/64)
# 11:  16384 Hz (OSC/256)


class Timer:
    def __init__(self):
        self.DIV = 0  # Always showing self.counter with mode 3 divider
        self.TIMA = 0  # Can be set from RAM 0xFF05
        self.DIV_counter = 0
        self.TIMA_counter = 0
        self.TMA = 0
        self.TAC = 0
        self.dividers = [10, 4, 6, 8]
        self._cycles_to_interrupt = 0
        self.last_cycles = 0

    def reset(self):
        # TODO: Should probably one be DIV=0, but this makes a bunch of mooneye tests pass
        self.DIV_counter = 0
        self.TIMA_counter = 0
        self.DIV = 0

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        self.DIV_counter += cycles
        self.DIV += self.DIV_counter >> 8  # Add overflown bits to DIV
        self.DIV_counter &= 0xFF  # Remove the overflown bits
        self.DIV &= 0xFF

        if self.TAC & 0b100 == 0:  # Check if timer is not enabled
            self._cycles_to_interrupt = MAX_CYCLES
            return False

        self.TIMA_counter += cycles
        divider = self.dividers[self.TAC & 0b11]

        ret = False
        while self.TIMA_counter >= (1 << divider):
            self.TIMA_counter -= 1 << divider  # Keeps possible remainder
            self.TIMA += 1

            if self.TIMA > 0xFF:
                self.TIMA = self.TMA
                self.TIMA &= 0xFF
                ret = True
        self._cycles_to_interrupt = ((0x100 - self.TIMA) << divider) - self.TIMA_counter
        return ret

    def save_state(self, f):
        f.write(self.DIV)
        f.write(self.TIMA)
        f.write_16bit(self.DIV_counter)
        f.write_16bit(self.TIMA_counter)
        f.write(self.TMA)
        f.write(self.TAC)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self._cycles_to_interrupt)

    def load_state(self, f, state_version):
        self.DIV = f.read()
        self.TIMA = f.read()
        self.DIV_counter = f.read_16bit()
        self.TIMA_counter = f.read_16bit()
        self.TMA = f.read()
        self.TAC = f.read()
        if state_version >= 12:
            self.last_cycles = f.read_64bit()
        if state_version >= 13:
            self._cycles_to_interrupt = f.read_64bit()
