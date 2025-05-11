#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.utils import MAX_CYCLES

CYCLES_8192HZ = 128


class Serial:
    def __init__(self):
        self.SB = 0xFF  # Always 0xFF for a disconnected link cable
        self.SC = 0
        self.transfer_enabled = 0
        self.internal_clock = 0
        self._cycles_to_interrupt = 0
        self.last_cycles = 0
        self.clock = 0
        self.clock_target = MAX_CYCLES

    def set_SB(self, value):
        # Always 0xFF when cable is disconnected. Connecting is not implemented yet.
        self.SB = 0xFF

    def set_SC(self, value):  # cgb, double_speed
        self.SC = value
        self.transfer_enabled = self.SC & 0x80
        # TODO:
        # if cgb and (self.SC & 0b10): # High speed transfer
        #     self.double_speed = ...
        self.internal_clock = self.SC & 1  # 0: external, 1: internal
        if self.internal_clock:
            self.clock_target = self.clock + 8 * CYCLES_8192HZ
        else:
            # Will never complete, as there is no connection
            self.transfer_enabled = 0  # Technically it is enabled, but no reason to track it.
            self.clock_target = MAX_CYCLES
        self._cycles_to_interrupt = self.clock_target - self.clock

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        self.clock += cycles

        interrupt = False
        if self.transfer_enabled and self.clock >= self.clock_target:
            self.SC &= 0x80
            self.transfer_enabled = 0
            # self._cycles_to_interrupt = MAX_CYCLES
            self.clock_target = MAX_CYCLES
            interrupt = True

        self._cycles_to_interrupt = self.clock_target - self.clock
        return interrupt

    def save_state(self, f):
        f.write(self.SB)
        f.write(self.SC)
        f.write(self.transfer_enabled)
        f.write(self.internal_clock)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self._cycles_to_interrupt)
        f.write_64bit(self.clock)
        f.write_64bit(self.clock_target)

    def load_state(self, f, state_version):
        self.SB = f.read()
        self.SC = f.read()
        self.transfer_enabled = f.read()
        self.internal_clock = f.read()
        self.last_cycles = f.read_64bit()
        self._cycles_to_interrupt = f.read_64bit()
        self.clock = f.read_64bit()
        self.clock_target = f.read_64bit()
