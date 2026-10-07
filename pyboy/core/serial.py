#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import threading
import contextlib
import io
import json
import base64
import hashlib
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
            self._cycles_to_interrupt = self.clock_target - self.clock
        else:
            # Will never complete, as there is no connection
            self.transfer_enabled = 0  # Technically it is enabled, but no reason to track it.
            self.clock_target = MAX_CYCLES
            # The clock keeps counting, so the distance to the MAX_CYCLES
            # sentinel would eventually go negative and stall the
            # coordinator loop at the minimum cycle target.
            self._cycles_to_interrupt = MAX_CYCLES

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

        if self.transfer_enabled:
            self._cycles_to_interrupt = self.clock_target - self.clock
        else:
            # The clock keeps counting, so the distance to the MAX_CYCLES
            # sentinel would eventually go negative and stall the
            # coordinator loop at the minimum cycle target.
            self._cycles_to_interrupt = MAX_CYCLES
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

    def _checkpoint_state(self, state=None):
        return None

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
        self.bits_transferred = 0

    def save_state(self, f):
        check = getattr(self.shared_memory, "_check_state_operation", None)
        if check is None:
            raise PyBoyInvalidOperationException("Save/load is not supported by this serial transport")
        check()
        Serial.save_state(self, f)

    def load_state(self, f, state_version):
        check = getattr(self.shared_memory, "_check_state_operation", None)
        if check is None:
            raise PyBoyInvalidOperationException("Save/load is not supported by this serial transport")
        check()
        Serial.load_state(self, f, state_version)

    def _checkpoint_state(self, state=None):
        if state is not None:
            self.bits_transferred = state["bits"]
        return {
            "slot": self.shared_slot,
            "interrupt": bool(self.interrupt_based),
            "cgb": bool(self.cgb_mode),
            "bits": self.bits_transferred,
        }

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
            self._cycles_to_interrupt = self.clock_target - self.clock
        else:
            self.clock_target = MAX_CYCLES
            # The clock keeps counting, so the distance to the MAX_CYCLES
            # sentinel would eventually go negative and stall the
            # coordinator loop at the minimum cycle target.
            self._cycles_to_interrupt = MAX_CYCLES

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

        if self.transfer_enabled:
            self._cycles_to_interrupt = self.clock_target - self.clock
        else:
            # The clock keeps counting, so the distance to the MAX_CYCLES
            # sentinel would eventually go negative and stall the
            # coordinator loop at the minimum cycle target.
            self._cycles_to_interrupt = MAX_CYCLES
        return interrupt

    def stop(self):
        pass


class SerialSharedMemoryBuffer:
    def __init__(self, name=None):
        self.connected = True
        # Shared across processes like the transfer barrier. The checkpoint
        # coordinator itself operates on two locally owned PyBoy objects.
        self._execution_lock = multiprocessing.RLock()
        self._active_ticks = multiprocessing.Value("i", 0, lock=False)
        self._checkpointing = multiprocessing.Value("b", False, lock=False)
        self._state_operation = False
        self._checkpoint_failed = multiprocessing.Value("b", False, lock=False)
        self.barrier = multiprocessing.Barrier(2)
        self._owner = name is None
        self._shared_memory = (
            shared_memory.SharedMemory(create=True, size=2) if name is None else shared_memory.SharedMemory(name=name)
        )

    def _enter_tick(self):
        with self._execution_lock:
            if self._checkpoint_failed.value:
                raise PyBoyInvalidOperationException("Serial rollback failed; discard both emulators")
            if self._checkpointing.value:
                raise PyBoyInvalidOperationException("Serial pair is being checkpointed")
            self._active_ticks.value += 1

    def _leave_tick(self):
        with self._execution_lock:
            self._active_ticks.value -= 1

    def _check_state_operation(self):
        if not self._state_operation:
            raise PyBoyInvalidOperationException("Use SerialSharedMemoryBuffer paired save_state/load_state")

    @contextlib.contextmanager
    def _checkpoint(self, peers):
        # Never wait for a tick: it may be waiting for its peer at a transfer
        # barrier. The caller must stop/join both execution workers first.
        with self._execution_lock:
            if self._active_ticks.value or self._checkpointing.value:
                raise PyBoyInvalidOperationException("Stop both serial workers before checkpointing")
            if not self.connected or self.barrier.broken or self.barrier.n_waiting:
                raise PyBoyInvalidOperationException("Serial transport is not at a connected boundary")
            if peers[0] is peers[1] or any(peer._serial_shared_memory is not self for peer in peers):
                raise PyBoyInvalidOperationException("Supply the two owners of this serial buffer")
            self._checkpointing.value = True
        try:
            self._state_operation = True
            yield
        finally:
            self._state_operation = False
            with self._execution_lock:
                self._checkpointing.value = False

    def _capture(self, peers):
        endpoints = []
        for peer in peers:
            stream = io.BytesIO()
            peer.save_state(stream)
            blob = stream.getvalue()
            endpoints.append(
                {
                    "state": base64.b64encode(blob).decode("ascii"),
                    "sha256": hashlib.sha256(blob).hexdigest(),
                    "runtime": peer._serial_checkpoint(),
                }
            )
        return {"version": 1, "transport": list(self._shared_memory.buf[:2]), "peers": endpoints}

    def save_state(self, left, right):
        """Return a paired checkpoint as bytes, with both tick workers stopped.

        Both emulators must be owned in this process and use this buffer (two
        threads can tick them). This does not halt or schedule emulation. Calls
        during a tick, a transfer rendezvous or a disconnect fail immediately.
        The caller owns all other emulator access and durable publication.
        """
        with self._checkpoint((left, right)):
            state = self._capture((left, right))
            self._validate((left, right), state)
            return json.dumps(state, sort_keys=True).encode("utf8")

    def _validate(self, peers, state):
        from pyboy.utils import STATE_VERSION

        if not isinstance(state, dict) or type(state.get("version")) is not int or state.get("version") != 1:
            raise ValueError("Unsupported serial checkpoint version")
        transport = state.get("transport")
        if (
            not isinstance(transport, list)
            or len(transport) != 2
            or any(type(value) is not int or not 0 <= value <= 255 for value in transport)
        ):
            raise ValueError("Invalid serial transport bytes")
        endpoints = state.get("peers")
        if not isinstance(endpoints, list) or len(endpoints) != 2:
            raise ValueError("A serial checkpoint needs both peers")
        slots = []
        blobs = []
        for peer, endpoint in zip(peers, endpoints):
            runtime = endpoint["runtime"]
            current = peer._serial_checkpoint()
            for key in ("rom", "slot", "interrupt", "cgb"):
                if runtime[key] != current[key] or type(runtime[key]) is not type(current[key]):
                    raise ValueError("Serial checkpoint cartridge order or configuration changed")
            slots.append(runtime["slot"])
            if type(runtime["bits"]) is not int or not 0 <= runtime["bits"] <= 8:
                raise ValueError("Invalid serial bit count")
            if type(runtime["frame"]) is not int or runtime["frame"] < 0:
                raise ValueError("Invalid frame counter")
            for event in runtime["events"]:
                if (
                    type(event) is not int
                    or not pyboy.utils.WindowEvent.PRESS_ARROW_UP
                    <= event
                    <= pyboy.utils.WindowEvent.RELEASE_BUTTON_START
                ):
                    raise ValueError("Invalid queued event")
            for frame, event in runtime["input"]:
                if (
                    type(frame) is not int
                    or frame < runtime["frame"]
                    or type(event) is not int
                    or not pyboy.utils.WindowEvent.PRESS_ARROW_UP
                    <= event
                    <= pyboy.utils.WindowEvent.RELEASE_BUTTON_START
                ):
                    raise ValueError("Invalid delayed input")
            blob = base64.b64decode(endpoint["state"], validate=True)
            if not blob or blob[0] != STATE_VERSION or hashlib.sha256(blob).hexdigest() != endpoint["sha256"]:
                raise ValueError("Serial checkpoint state version or checksum mismatch")
            blobs.append(blob)
        if sorted(slots) != [0, 1] or endpoints[0]["runtime"]["interrupt"] != endpoints[1]["runtime"]["interrupt"]:
            raise ValueError("Serial peers need opposite slots and matching transfer modes")
        return blobs

    def _restore(self, peers, state, blobs):
        # No worker can enter tick until both native states, bit counts, inputs
        # and transport bytes have been installed. The barrier is already idle;
        # never serialize or replace its OS synchronization primitives.
        for peer, endpoint, blob in zip(peers, state["peers"], blobs):
            peer.load_state(io.BytesIO(blob))
            peer._serial_checkpoint(endpoint["runtime"])
        self._shared_memory.buf[:2] = bytes(state["transport"])

    def load_state(self, left, right, checkpoint):
        """Restore both stopped workers, or roll both back on a load error.

        Cartridge order, transfer mode, slots, checksums and state version must
        match. A disconnected/broken transport cannot be revived by loading.
        If rollback itself fails, execution stays disabled: discard this pair.
        """
        peers = (left, right)
        with self._checkpoint(peers):
            state = json.loads(checkpoint)
            blobs = self._validate(peers, state)
            backup = self._capture(peers)
            backup_blobs = self._validate(peers, backup)
            try:
                self._restore(peers, state, blobs)
            except BaseException:
                try:
                    self._restore(peers, backup, backup_blobs)
                except BaseException:
                    self._checkpoint_failed.value = True
                    self.connected = False
                    self.barrier.abort()
                    raise PyBoyInvalidOperationException("Serial rollback failed; discard both emulators") from None
                raise

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
