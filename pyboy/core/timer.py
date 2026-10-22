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
        self._cycles_to_irq = MAX_CYCLES
        self.last_cycles = 0

    def reset(self):
        timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
        if self.TAC & 0b100 and self.DIV_counter & timer_bit:
            self._increase_tima()
        self.DIV_counter = 0
        self.DIV = 0
        self._update_cycles_to_irq()

    def _increase_tima(self):
        self.TIMA += 1
        if self.TIMA > 0xFF:
            self.TIMA = self.TMA
            self.tima_reload_state = 1
            self.TIMA_counter = 4

    def write_tima(self, value):
        if self.tima_reload_state != 2:
            self.TIMA = value
        self._update_cycles_to_irq()

    def write_tma(self, value):
        self.TMA = value
        if self.tima_reload_state != 0:
            self.TIMA = value
        self._update_cycles_to_irq()

    def write_tac(self, value):
        old_timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
        new_timer_bit = 1 << (self.dividers[value & 0b11] - 1)
        if self.TAC & 0b100 and self.DIV_counter & old_timer_bit:
            if not value & 0b100 or not self.DIV_counter & new_timer_bit:
                self._increase_tima()
        self.TAC = value & 0b111
        self._update_cycles_to_irq()

    def _update_cycles_to_irq(self):
        if self.tima_reload_state:
            # State 1 raises the interrupt; state 2 completes the four-cycle reload window.
            self._cycles_to_irq = self.TIMA_counter if self.TIMA_counter else 1
        elif self.TAC & 0b100:
            timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
            period = timer_bit * 2
            counter = self.DIV_counter
            next_edge = period - (counter & (period - 1))
            cycles_to_irq = next_edge + (0xFF - self.TIMA) * period + 4
            self._cycles_to_irq = cycles_to_irq
        else:
            self._cycles_to_irq = MAX_CYCLES

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
                    self._update_cycles_to_irq()
                    return False
            else:
                self.DIV_counter = (self.DIV_counter + cycles) & 0xFFFF
                self.DIV = self.DIV_counter >> 8
                self._update_cycles_to_irq()
                return False

        # Slow path: a TIMA reload is in progress, or TIMA overflows within
        # this tick. Advance one cycle at a time as on hardware.
        ret = False
        timer_enabled = self.TAC & 0b100
        if timer_enabled:
            timer_bit = 1 << (self.dividers[self.TAC & 0b11] - 1)
            period = timer_bit * 2
        else:
            timer_bit = 0
            period = 0

        while cycles:
            counter = self.DIV_counter
            if self.tima_reload_state:
                steps = cycles
                next_edge = 0
                if timer_enabled:
                    next_edge = period - (counter & (period - 1))
                    if next_edge < steps:
                        steps = next_edge
                if self.TIMA_counter and self.TIMA_counter < steps:
                    steps = self.TIMA_counter

                timer_edge = timer_enabled and next_edge == steps
                self.TIMA_counter -= steps
                if self.TIMA_counter == 0:
                    if self.tima_reload_state == 1:
                        self.tima_reload_state = 2
                        self.TIMA_counter = 4
                        ret = True
                    else:
                        self.tima_reload_state = 0

                new_counter = (counter + steps) & 0xFFFF
                self.DIV_counter = new_counter
                self.DIV = new_counter >> 8
                if timer_edge:
                    self._increase_tima()
                cycles -= steps
                continue

            if not timer_enabled:
                self.DIV_counter = (counter + cycles) & 0xFFFF
                self.DIV = self.DIV_counter >> 8
                cycles = 0
                continue

            next_edge = period - (counter & (period - 1))
            edge_count = 0
            if cycles >= next_edge:
                edge_count = 1 + (cycles - next_edge) // period

            increments_to_overflow = 0x100 - self.TIMA
            if edge_count < increments_to_overflow:
                self.TIMA += edge_count
                steps = cycles
            else:
                steps = next_edge + (increments_to_overflow - 1) * period
                self.TIMA = 0xFF
                self._increase_tima()

            new_counter = (counter + steps) & 0xFFFF
            self.DIV_counter = new_counter
            self.DIV = new_counter >> 8
            cycles -= steps

        self._update_cycles_to_irq()
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
        # Keep the legacy cached-deadline slot in the save-state stream.
        f.write_64bit(self._cycles_to_irq)

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
            f.read_64bit()
        self._update_cycles_to_irq()
