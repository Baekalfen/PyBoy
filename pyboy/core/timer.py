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
        self.tima_reload_state = 0
        self._cycles_to_interrupt = 0
        self.last_cycles = 0

    def reset(self):
        timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
        if self.TAC & 0b100 and self.DIV_counter & timer_bit:
            self._increase_tima()
        self.DIV_counter = 0
        self.DIV = 0

    def _increase_tima(self):
        self.TIMA += 1
        if self.TIMA > 0xFF:
            self.TIMA = self.TMA
            self.tima_reload_state = 1
            self.TIMA_counter = 4

    def write_tima(self, value):
        if self.tima_reload_state != 2:
            self.TIMA = value

    def write_tma(self, value):
        self.TMA = value
        if self.tima_reload_state != 0:
            self.TIMA = value

    def write_tac(self, value):
        old_timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
        new_timer_bit = 1 << (self.dividers[value & 0b11] - 1)
        if self.TAC & 0b100 and self.DIV_counter & old_timer_bit:
            if not value & 0b100 or not self.DIV_counter & new_timer_bit:
                self._increase_tima()
        self.TAC = value & 0b111

    def read_tima(self):
        if self.tima_reload_state == 1:
            return 0
        return self.TIMA

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        ret = False
        while cycles:
            if self.tima_reload_state:
                self.TIMA_counter -= 1
                if self.TIMA_counter == 0:
                    if self.tima_reload_state == 1:
                        self.tima_reload_state = 2
                        self.TIMA_counter = 4
                        ret = True
                    else:
                        self.tima_reload_state = 0

            counter = self.DIV_counter
            new_counter = (counter + 1) & 0xFFFF
            timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
            if self.TAC & 0b100 and counter & timer_bit and not new_counter & timer_bit:
                self._increase_tima()

            self.DIV_counter = new_counter
            self.DIV = new_counter >> 8
            cycles -= 1

        if self.TAC & 0b100:
            timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
            next_edge = ((self.DIV_counter & ~(timer_bit * 2 - 1)) + timer_bit * 2) - self.DIV_counter
            self._cycles_to_interrupt = next_edge
            if self.tima_reload_state:
                self._cycles_to_interrupt = min(self._cycles_to_interrupt, self.TIMA_counter)
        else:
            self._cycles_to_interrupt = MAX_CYCLES
        return ret

    def save_state(self, f):
        f.write(self.DIV)
        f.write(self.TIMA)
        f.write_16bit(self.DIV_counter)
        f.write_16bit(self.TIMA_counter)
        f.write(self.TMA)
        f.write(self.TAC)
        f.write(self.tima_reload_state)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self._cycles_to_interrupt)

    def load_state(self, f, state_version):
        self.DIV = f.read()
        self.TIMA = f.read()
        self.DIV_counter = f.read_16bit()
        self.TIMA_counter = f.read_16bit()
        self.TMA = f.read()
        self.TAC = f.read()
        if state_version >= 20:
            self.tima_reload_state = f.read()
        else:
            self.tima_reload_state = 0
        if state_version >= 12:
            self.last_cycles = f.read_64bit()
        if state_version >= 13:
            self._cycles_to_interrupt = f.read_64bit()
