#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

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
        self.DIV = 0 # Always showing self.counter with mode 3 divider
        self.TIMA = 0 # Can be set from RAM 0xFF05
        self.DIV_counter = 0
        self.TIMA_counter = 0
        self.TMA = 0
        self.TAC = 0
        self.dividers = [1024, 16, 64, 256]

    def tick(self, cycles):
        self.DIV_counter += cycles
        self.DIV += (self.DIV_counter >> 8) # Add overflown bits to DIV
        self.DIV_counter &= 0xFF # Remove the overflown bits
        self.DIV &= 0xFF

        if self.TAC & 0b100 == 0: # Check if timer is not enabled
            return False

        self.TIMA_counter += cycles
        divider = self.dividers[self.TAC & 0b11]

        if self.TIMA_counter >= divider:
            self.TIMA_counter -= divider # Keeps possible remainder
            self.TIMA += 1

            if self.TIMA > 0xFF:
                self.TIMA = self.TMA
                self.TIMA &= 0xFF
                return True

        return False

    def cyclestointerrupt(self):
        if self.TAC & 0b100 == 0: # Check if timer is not enabled
            # Large enough, that 'calculate_cycles' will choose 'x'
            return 1 << 16

        divider = self.dividers[self.TAC & 0b11]

        cyclesleft = ((0x100 - self.TIMA) * divider) - self.TIMA_counter

        return cyclesleft

    def save_state(self, f):
        f.write(self.DIV)
        f.write(self.TIMA)
        f.write_16bit(self.DIV_counter)
        f.write_16bit(self.TIMA_counter)
        f.write(self.TMA)
        f.write(self.TAC)

    def load_state(self, f, state_version):
        self.DIV = f.read()
        self.TIMA = f.read()
        self.DIV_counter = f.read_16bit()
        self.TIMA_counter = f.read_16bit()
        self.TMA = f.read()
        self.TAC = f.read()
