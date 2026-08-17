#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import threading
import multiprocessing
from multiprocessing import shared_memory
import pyboy
from pyboy.utils import MAX_CYCLES, PyBoyInvalidOperationException

logger = pyboy.logging.get_logger(__name__)

try:
    import cython
except ImportError:

    class _mock:
        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    exec(
        """
class cython:
    gil = _mock()
    nogil = _mock()
""",
        globals(),
        locals(),
    )


CYCLES_8192HZ = 128


class Serial:
    def __init__(self, cgb_mode):
        self.cgb_mode = cgb_mode  # Indicates if we are CGB hardware, running in CGB or DMG mode
        self.SB = 0xFF  # Always 0xFF for a disconnected link cable
        if self.cgb_mode:
            self.SC = 0b01111100
        else:
            self.SC = 0b01111110
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
        if self.cgb_mode:
            self.SC = value | 0b01111100  # Mask out read-only bits
        else:
            self.SC = value | 0b01111110  # Mask out read-only bits
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
            # Clear bit 7 (transfer in progress). Games poll this bit to
            # detect transfer completion.
            self.SC &= 0b01111111
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

    def stop(self):
        pass


class SerialSharedMemory(Serial):
    def __init__(self, cgb_mode, shared_memory, serial_interrupt_based):
        super().__init__(cgb_mode)
        self.shared_memory = shared_memory
        self.shared_slot = self.shared_memory.read(0)
        if self.shared_slot == 0:
            self.shared_memory.write(self.shared_slot, 1)

        self.shared_memory.synchronize()
        self.shared_memory.write(self.shared_slot, 0)

        self.interrupt_based = serial_interrupt_based

    def save_state(self, f):
        raise PyBoyInvalidOperationException("Save state is not supported with serial connection")

    def load_state(self, f, state_version):
        raise PyBoyInvalidOperationException("Load state is not supported with serial connection")

    def set_SB(self, value):
        self.SB = value

    def set_SC(self, value):
        if self.cgb_mode:
            self.SC = value | 0b01111100
        else:
            self.SC = value | 0b01111110
        self.transfer_enabled = self.SC & 0x80
        self.internal_clock = self.SC & 1
        self.bits_transferred = 0
        if self.transfer_enabled:
            if self.interrupt_based:
                self.clock_target = self.clock + CYCLES_8192HZ * 8
            else:
                self.clock_target = self.clock + CYCLES_8192HZ
        else:
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
            with cython.gil:
                if self.interrupt_based:
                    self.shared_memory.write(self.shared_slot, self.SB)
                    self.shared_memory.synchronize()
                    self.SB = self.shared_memory.read(1 - self.shared_slot)
                    self.shared_memory.synchronize()
                    self.bits_transferred = 8
                else:
                    # logger.debug("Sending %x", self.SB)
                    self.shared_memory.write(self.shared_slot, (self.SB & 0x80) >> 7)
                    # logger.debug("Sending sync")
                    self.shared_memory.synchronize()
                    # logger.debug("Reading")
                    self.SB <<= 1
                    self.SB &= 0xFF
                    self.SB |= self.shared_memory.read(1 - self.shared_slot) & 1
                    # logger.debug("Reading sync")
                    self.shared_memory.synchronize()
                    self.bits_transferred += 1

                if self.bits_transferred == 8:
                    self.SC &= 0b0111_1111
                    interrupt = True
                    self.clock_target = MAX_CYCLES
                    self.transfer_enabled = 0
                else:
                    self.clock_target = self.clock + CYCLES_8192HZ

        self._cycles_to_interrupt = self.clock_target - self.clock
        return interrupt

    def stop(self):
        pass


class SerialSharedMemoryBuffer:
    def __init__(self, name=None):
        self.connected = True
        self.barrier = multiprocessing.Barrier(2)
        self._owner = name is None
        self._shared_memory = (
            shared_memory.SharedMemory(create=True, size=2) if name is None else shared_memory.SharedMemory(name=name)
        )

    def write(self, slot, value):
        if self.connected:
            self._shared_memory.buf[slot] = value

    def read(self, slot):
        if self.connected:
            return self._shared_memory.buf[slot]
        else:
            return 1

    def synchronize(self):
        if self.connected:
            try:
                self.barrier.wait(timeout=30)
            except threading.BrokenBarrierError:
                logger.error("Connection lost to the other emulator")
                self.connected = False  # TODO: Reconnect?

    def __del__(self):
        self.close()

    def close(self):
        self._shared_memory.close()
        try:
            self._shared_memory.unlink()
        except FileNotFoundError:
            pass
