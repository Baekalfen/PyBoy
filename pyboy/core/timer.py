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

        timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)

        # Fast path: no TIMA reload in progress. The DIV counter and TIMA
        # can then be advanced arithmetically, unless TIMA overflows within
        # this tick. A falling edge of timer_bit happens when the counter
        # goes from having the bit set to having it cleared, which is at
        # counter values congruent to (2*timer_bit - 1) modulo 2*timer_bit.
        # All timer periods (16, 64, 256, 1024) divide 2**16, so the
        # congruence is unaffected by the counter wrapping at 0xFFFF.
        if self.tima_reload_state == 0:
            if self.TAC & 0b100:
                period = timer_bit * 2
                mask = period - 1
                start = self.DIV_counter
                end = start + cycles
                # One period is added to both terms to keep the divisions
                # on non-negative numbers only.
                tima_increases = (end - 1 - mask + period) // period - (start - 1 - mask + period) // period
                if self.TIMA + tima_increases <= 0xFF:
                    self.TIMA += tima_increases
                    self.DIV_counter = end & 0xFFFF
                    self.DIV = self.DIV_counter >> 8
                    next_edge = ((self.DIV_counter & ~(period - 1)) + period) - self.DIV_counter
                    # The CPU only needs to wake for the TIMA overflow
                    # interrupt, not for every TIMA increment.
                    self._cycles_to_interrupt = next_edge + (0xFF - self.TIMA) * period
                    return False
            else:
                self.DIV_counter = (self.DIV_counter + cycles) & 0xFFFF
                self.DIV = self.DIV_counter >> 8
                self._cycles_to_interrupt = MAX_CYCLES
                return False

        # Slow path: a TIMA reload is in progress, or TIMA overflows within
        # this tick. Advance one cycle at a time as on hardware.
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
            if self.TAC & 0b100 and counter & timer_bit and not new_counter & timer_bit:
                self._increase_tima()

            self.DIV_counter = new_counter
            self.DIV = new_counter >> 8
            cycles -= 1

        if self.TAC & 0b100:
            period = timer_bit * 2
            next_edge = ((self.DIV_counter & ~(period - 1)) + period) - self.DIV_counter
            # The CPU only needs to wake for the TIMA overflow interrupt,
            # not for every TIMA increment. While a reload is pending in
            # state 1, the interrupt flag is raised when TIMA_counter
            # expires.
            self._cycles_to_interrupt = next_edge + (0xFF - self.TIMA) * period
            if self.tima_reload_state == 1:
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
