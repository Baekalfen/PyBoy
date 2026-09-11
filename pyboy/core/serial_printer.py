#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.core.serial import Serial
from pyboy.utils import MAX_CYCLES


class SerialPrinter(Serial):
    def __init__(self, cgb_mode, printer):
        super().__init__(cgb_mode)
        self.printer = printer
        self._outgoing_byte = 0
        self._pending_response = 0

    def set_SB(self, value):
        self._outgoing_byte = value

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles
        self.clock += cycles

        interrupt = False
        if self.transfer_enabled and self.clock >= self.clock_target:
            self.SC &= 0b01111111
            self.transfer_enabled = 0
            self.clock_target = MAX_CYCLES
            # Printer response to a byte is read during the following transfer.
            self.SB = self._pending_response
            self.printer.process_byte_nogil(self._outgoing_byte)
            self._pending_response = self.printer.response_byte
            interrupt = True

        self._cycles_to_interrupt = self.clock_target - self.clock
        return interrupt

    def save_state(self, f):
        super().save_state(f)
        f.write(self._outgoing_byte)
        f.write(self._pending_response)

    def load_state(self, f, state_version):
        super().load_state(f, state_version)
        self._outgoing_byte = f.read()
        self._pending_response = f.read()

    def stop(self):
        self.printer.stop()
