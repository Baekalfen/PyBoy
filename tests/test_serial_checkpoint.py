"""Paired checkpoints extend the existing shared-memory serial transport."""

import io
import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from pyboy import PyBoy
from pyboy.core.serial import SerialSharedMemory, SerialSharedMemoryBuffer
from pyboy.utils import IntIOWrapper, PyBoyInvalidOperationException, STATE_VERSION, cython_compiled


def together(left, right, timeout=5):
    with ThreadPoolExecutor(2) as workers:
        futures = [workers.submit(call) for call in (left, right)]
        return [future.result(timeout=timeout) for future in futures]


def open_pair(buffer, interrupt=False):
    def make():
        p = PyBoy(
            "pyboy/default_rom.gb",
            window="null",
            sound_emulated=False,
            serial_shared_memory=buffer,
            serial_interrupt_based=interrupt,
        )
        p.set_emulation_speed(0)
        return p

    # Existing slot allocation uses the first peer's slot-0 publication.
    with ThreadPoolExecutor(2) as workers:
        first = workers.submit(make)
        deadline = threading.Event()
        for _ in range(500):
            if buffer.read(0) == 1:
                break
            deadline.wait(0.001)
        else:
            buffer.barrier.abort()
            raise AssertionError("First peer did not publish its slot")
        second = workers.submit(make)
        return first.result(timeout=5), second.result(timeout=5)


@pytest.fixture
def pair():
    buffer = SerialSharedMemoryBuffer()
    peers = open_pair(buffer)
    try:
        yield buffer, peers
    finally:
        for peer in peers:
            peer.stop(save=False)
        buffer.close()


@pytest.mark.parametrize("interrupt", [False, True])
def test_cold_pair_restores_native_state_transport_and_delayed_input(interrupt):
    buffer = SerialSharedMemoryBuffer()
    peers = open_pair(buffer, interrupt)
    try:
        # Warm boot uses both ordinary tick paths, with no custom scheduler.
        together(lambda: peers[0].tick(70, False, False), lambda: peers[1].tick(70, False, False))
        for index, peer in enumerate(peers):
            peer.memory[0xC000] = 42 + index
            peer.button("a", 3)
            peer.memory[0xFF01] = [0xA5, 0x5A][index]
            peer.memory[0xFF02] = 0x81 if index == 0 else 0x80
        checkpoint = buffer.save_state(*peers)
        together(lambda: peers[0].tick(1, False, False), lambda: peers[1].tick(1, False, False))
        assert [p.memory[0xFF01] for p in peers] == [0x5A, 0xA5]
        assert not any(p.memory[0xFF02] & 0x80 for p in peers)
        expected = json.loads(buffer.save_state(*peers))
    finally:
        for peer in peers:
            peer.stop(save=False)
        buffer.close()
    fresh = SerialSharedMemoryBuffer()
    restored = open_pair(fresh, interrupt)
    try:
        fresh.load_state(*restored, checkpoint)
        assert [p.memory[0xC000] for p in restored] == [42, 43]
        assert json.loads(fresh.save_state(*restored)) == json.loads(checkpoint)
        together(lambda: restored[0].tick(1, False, False), lambda: restored[1].tick(1, False, False))
        assert json.loads(fresh.save_state(*restored)) == expected
        together(lambda: restored[0].tick(3, False, False), lambda: restored[1].tick(3, False, False))
        assert all(not p._serial_checkpoint()["input"] for p in restored)
        for peer in restored:
            peer.memory[0xFF00] = 0x10  # Select action buttons
            assert peer.memory[0xFF00] & 1  # A was actually released
    finally:
        for peer in restored:
            peer.stop(save=False)
        fresh.close()


def test_individual_state_operations_reject_before_write_or_mutation(pair):
    buffer, peers = pair
    f = io.BytesIO()
    with pytest.raises(PyBoyInvalidOperationException, match="paired"):
        peers[0].save_state(f)
    assert not f.getvalue()
    before = buffer.save_state(*peers)
    with pytest.raises(PyBoyInvalidOperationException, match="paired"):
        peers[0].load_state(io.BytesIO(b"bad"))
    assert buffer.save_state(*peers) == before


@pytest.mark.parametrize("operation", ["save", "load"])
def test_busy_worker_fails_without_waiting_or_mutating(pair, operation):
    buffer, peers = pair
    checkpoint = buffer.save_state(*peers)
    buffer._enter_tick()
    try:
        with pytest.raises(PyBoyInvalidOperationException, match="Stop both"):
            if operation == "save":
                buffer.save_state(*peers)
            else:
                buffer.load_state(*peers, checkpoint)
    finally:
        buffer._leave_tick()
    assert buffer.save_state(*peers) == checkpoint


def test_real_worker_at_transfer_barrier_is_not_a_checkpoint_boundary(pair):
    buffer, peers = pair
    peers[0].memory[0xFF01] = 0xA5
    peers[0].memory[0xFF02] = 0x81
    with ThreadPoolExecutor(2) as workers:
        first = workers.submit(peers[0].tick, 70, False, False)
        for _ in range(500):
            if buffer.barrier.n_waiting:
                break
            threading.Event().wait(0.001)
        else:
            buffer.barrier.abort()
            raise AssertionError("Worker did not reach serial rendezvous")
        with pytest.raises(PyBoyInvalidOperationException, match="Stop both"):
            buffer.save_state(*peers)
        # Supply the peer instead of turning a pending bit into a checkpoint.
        peers[1].memory[0xFF01] = 0x5A
        peers[1].memory[0xFF02] = 0x80
        second = workers.submit(peers[1].tick, 70, False, False)
        first.result(timeout=5)
        second.result(timeout=5)
    buffer.save_state(*peers)


@pytest.mark.parametrize("damage", ["version", "checksum", "bits", "slot", "interrupt", "rom", "input", "transport"])
def test_invalid_pair_is_rejected_before_mutation(pair, damage):
    buffer, peers = pair
    original = buffer.save_state(*peers)
    state = json.loads(original)
    if damage == "version":
        state["version"] = 999
    elif damage == "checksum":
        state["peers"][1]["sha256"] = "wrong"
    elif damage == "transport":
        state["transport"] = [999, 0]
    else:
        runtime = state["peers"][1]["runtime"]
        runtime[damage] = {"bits": 9, "slot": 0, "interrupt": True, "rom": "wrong", "input": [[-1, 999]]}[damage]
    with pytest.raises(ValueError):
        buffer.load_state(*peers, json.dumps(state).encode())
    assert buffer.save_state(*peers) == original


def test_disconnected_and_broken_pairs_cannot_be_checkpointed(pair):
    buffer, peers = pair
    buffer.connected = False
    with pytest.raises(PyBoyInvalidOperationException, match="connected"):
        buffer.save_state(*peers)
    buffer.connected = True
    buffer.barrier.abort()
    with pytest.raises(PyBoyInvalidOperationException, match="connected"):
        buffer.save_state(*peers)


def test_tick_is_excluded_for_entire_checkpoint(pair):
    buffer, peers = pair
    with buffer._checkpoint(peers):
        with pytest.raises(PyBoyInvalidOperationException, match="being checkpointed"):
            peers[0].tick(0)
    peers[0].tick(0)


@pytest.mark.skipif(cython_compiled, reason="Direct serial unit access is private in compiled builds")
@pytest.mark.parametrize("bits", range(9))
def test_every_partial_byte_resumes_with_base_timing_and_bit_count(bits):
    buffer = SerialSharedMemoryBuffer()
    # Same ordered construction as PyBoy, but unit-level access to serial.tick.
    with ThreadPoolExecutor(2) as workers:
        first = workers.submit(SerialSharedMemory, False, buffer, False)
        for _ in range(500):
            if buffer.read(0) == 1:
                break
            threading.Event().wait(0.001)
        second = workers.submit(SerialSharedMemory, False, buffer, False)
        ports = first.result(timeout=5), second.result(timeout=5)
    try:
        for index, port in enumerate(ports):
            port.set_SB([0xA5, 0x5A][index])
            port.set_SC(0x81 if index == 0 else 0x80)

        def tick_bit(cycle):
            return together(lambda: ports[0].tick(cycle), lambda: ports[1].tick(cycle))

        for bit in range(bits):
            tick_bit((bit + 1) * 128)
        snapshots = []
        metadata = []
        with buffer._execution_lock:
            buffer._state_operation = True
            for port in ports:
                f = io.BytesIO()
                port.save_state(IntIOWrapper(f))
                snapshots.append(f.getvalue())
                metadata.append(port._checkpoint_state())
            transport = bytes(buffer._shared_memory.buf[:2])
            buffer._state_operation = False
        for bit in range(bits, 8):
            interrupts = tick_bit((bit + 1) * 128)
            assert interrupts == [bit == 7, bit == 7]
        expected = [(p.SB, p.SC, p.clock, p.clock_target) for p in ports]
        buffer._state_operation = True
        for port, blob, extra in zip(ports, snapshots, metadata):
            port.load_state(IntIOWrapper(io.BytesIO(blob)), STATE_VERSION)
            port._checkpoint_state(extra)
        buffer._shared_memory.buf[:2] = transport
        buffer._state_operation = False
        for bit in range(bits, 8):
            interrupts = tick_bit((bit + 1) * 128)
            assert interrupts == [bit == 7, bit == 7]
        assert [(p.SB, p.SC, p.clock, p.clock_target) for p in ports] == expected
        assert [p.SB for p in ports] == [0x5A, 0xA5]
    finally:
        buffer.close()


def test_second_peer_load_failure_rolls_back_both_native_states_and_inputs(pair):
    buffer, peers = pair
    checkpoint = buffer.save_state(*peers)
    peers[0].memory[0xC000] = 99
    peers[1].button("b", 4)
    before = buffer.save_state(*peers)

    class FailingPeer:
        _serial_shared_memory = buffer
        failed = False

        def _serial_checkpoint(self, state=None):
            return peers[1]._serial_checkpoint(state)

        def save_state(self, stream):
            return peers[1].save_state(stream)

        def load_state(self, stream):
            peers[1].load_state(stream)
            if not self.failed:
                self.failed = True
                raise RuntimeError("Injected second-peer failure after mutation")

    with pytest.raises(RuntimeError, match="Injected"):
        buffer.load_state(peers[0], FailingPeer(), checkpoint)
    assert buffer.save_state(*peers) == before


def test_peer_order_and_duplicate_owner_are_rejected(pair):
    buffer, peers = pair
    checkpoint = buffer.save_state(*peers)
    with pytest.raises(ValueError, match="order"):
        buffer.load_state(peers[1], peers[0], checkpoint)
    with pytest.raises(PyBoyInvalidOperationException, match="two owners"):
        buffer.save_state(peers[0], peers[0])
    assert buffer.save_state(*peers) == checkpoint


def test_checkpoint_can_resume_in_another_process(pair, tmp_path):
    import os
    import subprocess
    import sys

    buffer, peers = pair
    for index, peer in enumerate(peers):
        peer.memory[0xFF01] = [0xA5, 0x5A][index]
        peer.memory[0xFF02] = 0x81 if index == 0 else 0x80
        peer.button("a", 3)
    path = tmp_path / "pair.json"
    path.write_bytes(buffer.save_state(*peers))
    script = """
import sys
from tests.test_serial_checkpoint import open_pair, together
from pyboy.core.serial import SerialSharedMemoryBuffer
buffer = SerialSharedMemoryBuffer()
peers = open_pair(buffer)
try:
    with open(sys.argv[1], 'rb') as stream:
        checkpoint = stream.read()
    buffer.load_state(*peers, checkpoint)
    assert buffer.save_state(*peers) == checkpoint
    together(lambda: peers[0].tick(70, False, False), lambda: peers[1].tick(70, False, False))
    assert [p.memory[0xFF01] for p in peers] == [0x5A, 0xA5]
    assert not any(p.memory[0xFF02] & 0x80 for p in peers)
finally:
    for p in peers:
        p.stop(save=False)
    buffer.close()
"""
    subprocess.run([sys.executable, "-c", script, str(path)], env=os.environ.copy(), check=True, timeout=30)


def test_failed_rollback_disables_execution(pair):
    buffer, peers = pair
    checkpoint = buffer.save_state(*peers)

    class BrokenPeer:
        _serial_shared_memory = buffer

        def _serial_checkpoint(self, state=None):
            return peers[1]._serial_checkpoint(state)

        def save_state(self, stream):
            return peers[1].save_state(stream)

        def load_state(self, stream):
            raise RuntimeError("Unrecoverable endpoint")

    with pytest.raises(PyBoyInvalidOperationException, match="rollback failed"):
        buffer.load_state(peers[0], BrokenPeer(), checkpoint)
    with pytest.raises(PyBoyInvalidOperationException, match="discard"):
        peers[0].tick(0)


def test_standalone_native_state_format_and_operations_are_unchanged():
    peer = PyBoy("pyboy/default_rom.gb", window="null", sound_emulated=False)
    try:
        stream = io.BytesIO()
        peer.save_state(stream)
        assert stream.getvalue()[0] == STATE_VERSION
        peer.memory[0xC000] = 123
        peer.load_state(io.BytesIO(stream.getvalue()))
        restored = io.BytesIO()
        peer.save_state(restored)
        assert restored.getvalue() == stream.getvalue()
    finally:
        peer.stop(save=False)


@pytest.mark.parametrize("event", [19, 24, 33])
def test_pending_emulator_control_events_are_not_checkpointable(pair, event):
    buffer, peers = pair
    peers[0].send_input(event)
    with pytest.raises(ValueError, match="event"):
        buffer.save_state(*peers)
