#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Experimental, same-process link cable with joint execution and save states.

Create two PyBoy instances with no_input=True, then attach them to LinkCable.
Use the cable to advance or save/load the pair; the individual button and memory
APIs remain available. The caller serializes access to both endpoints. Only
halt() may be called concurrently with execution. No background thread advances
either machine. Shared-memory serial connections cannot be attached here.

Normal-speed serial is serviced at CPU instruction boundaries. Fast CGB serial
and debugger hooks are rejected. This is not cycle-accurate fast serial support.
"""

import hashlib
import json
import threading
from zipfile import BadZipFile, ZIP_STORED, ZipFile

from .utils import STATE_VERSION, PyBoyInvalidInputException, PyBoyInvalidOperationException, WindowEvent

FRAME_CYCLES = 70224
STATE_FORMAT = "pyboy-link-1"
MAX_STATE_BYTES = 4 * 1024 * 1024


class LinkCable:
    """Own two emulators until close(), without taking ownership of their files.

    tick() advances frame periods, advance() advances base-speed T cycles, and
    step() executes one instruction (or one bounded hardware step). These return
    False while halted. Input is delivered through each endpoint's button API.
    Use set_emulation_speed(0) on both endpoints when externally pacing execution.

    disconnect() removes the wire but retains joint execution/state ownership.
    close() abandons any transfer and releases the endpoints for ordinary tick().
    It does not stop the emulators or write cartridge saves.
    """

    def __init__(self, left, right):
        if left is right:
            raise PyBoyInvalidInputException("A cable requires two distinct endpoints")
        self.machines = (left, right)
        self._owner = object()
        self._lock = threading.RLock()
        self._halt = threading.Event()
        self._closed = False
        self._connected = True
        self._cycles = [0, 0]
        self._epochs = [-1, -1]
        self._bits = [0, 0]
        self._edges = [None, None]
        self._transfers = [0, 0]
        for machine in self.machines:
            machine._link_validate(attaching=True)
        left._link_attach(self._owner)
        try:
            right._link_attach(self._owner)
        except BaseException:
            left._link_detach(self._owner)
            raise

    @property
    def cycles(self):
        """Elapsed base-speed T cycles for each endpoint, relative to attachment."""
        return tuple(self._cycles)

    @property
    def transfers(self):
        """Completed serial bytes on each endpoint."""
        return tuple(self._transfers)

    @property
    def connected(self):
        return self._connected

    @property
    def halted(self):
        return self._halt.is_set()

    def halt(self):
        """Request a hold at the next instruction boundary; safe from another thread."""
        self._halt.set()

    def resume(self):
        with self._lock:
            self._require_open()
            self._halt.clear()

    def disconnect(self):
        """Remove the wire. Internal-clock ports read high; external ports wait."""
        with self._lock:
            self._require_open()
            self._connected = False

    def connect(self):
        with self._lock:
            self._require_open()
            self._connected = True

    def tick(self, count=1, render=True, sound=True):
        """Advance count periods of 70224 base T cycles, without skipping frames."""
        _integer(count, 1)
        return self.advance(count * FRAME_CYCLES, render, sound)

    def advance(self, cycles, render=True, sound=True):
        """Advance both endpoints by at least cycles base T cycles, unless halted.

        Each endpoint may overshoot by one instruction/hardware step. Render and
        sound settings take effect at the next frame boundary. Audio is exposed
        through the ordinary sound buffer; tick one frame at a time to collect it.
        """
        _integer(cycles, 1)
        with self._lock:
            self._require_open()
            for machine in self.machines:
                machine._link_validate()
            target = min(self._cycles) + cycles
            while min(self._cycles) < target:
                if self._halt.is_set():
                    return False
                self._step(render, sound)
            self._wire()
            return True

    def step(self, render=True, sound=True):
        """Advance the earlier endpoint by one instruction/hardware step."""
        with self._lock:
            self._require_open()
            if self._halt.is_set():
                return False
            for machine in self.machines:
                machine._link_validate()
            self._step(render, sound)
            self._wire()
            return True

    def _step(self, render, sound):
        self._wire()
        side = 0 if self._cycles[0] <= self._cycles[1] else 1
        elapsed = self.machines[side]._link_step(self._owner, render, sound)
        if elapsed <= 0:
            raise PyBoyInvalidOperationException("Cable endpoint made no progress")
        self._cycles[side] += elapsed

    def _wire(self):
        ports = [machine._link_port() for machine in self.machines]
        for side, (_, control, epoch, double, cgb_mode) in enumerate(ports):
            if control & 0x80 and cgb_mode and control & 2:
                self.halt()
                raise PyBoyInvalidOperationException("Fast CGB serial is unsupported by LinkCable")
            if epoch != self._epochs[side]:
                self._epochs[side] = epoch
                self._bits[side] = 0
                self._edges[side] = self._cycles[side] + (256 if double else 512) if control & 0x81 == 0x81 else None
            if not control & 0x80:
                self._edges[side] = None
        for master in (0, 1):
            if self._edges[master] is None or self._edges[master] > min(self._cycles):
                continue
            active = [
                side
                for side in (0, 1)
                if ports[side][1] & 0x80 and (side == master or (self._connected and not ports[side][1] & 1))
            ]
            # Sample both outgoing bits before either shift register is changed.
            for side in active:
                incoming = (ports[1 - side][0] >> 7) & 1 if self._connected else 1
                self._bits[side] += 1
                complete = self._bits[side] == 8
                self.machines[side]._link_edge(self._owner, incoming, complete)
                if complete:
                    self._transfers[side] += 1
                    self._edges[side] = None
            if self._edges[master] is not None:
                self._edges[master] += 256 if ports[master][3] else 512

    def save_state(self, file_like_object):
        """Write both machines, serial timing and queued inputs as one archive.

        The file-like object must be binary. Publishing a file atomically remains
        the application's responsibility. This format is separate from individual
        PyBoy states. RTC behavior follows PyBoy's existing clock policy.
        """
        with self._lock:
            self._require_open()
            endpoints = [machine._link_snapshot(self._owner) for machine in self.machines]
            metadata = {
                "format": STATE_FORMAT,
                "state_version": STATE_VERSION,
                "identities": [list(machine._link_identity()) for machine in self.machines],
                "cycles": self._cycles,
                "epochs": self._epochs,
                "bits": self._bits,
                "edges": self._edges,
                "transfers": self._transfers,
                "connected": self._connected,
                "halted": self.halted,
                "runtime": [runtime for _, runtime in endpoints],
                "sha256": [hashlib.sha256(state).hexdigest() for state, _ in endpoints],
            }
            with ZipFile(file_like_object, "w", compression=ZIP_STORED) as archive:
                archive.writestr("cable.json", json.dumps(metadata, sort_keys=True))
                for side, (state, _) in enumerate(endpoints):
                    archive.writestr(f"{side}.state", state)

    def load_state(self, file_like_object):
        """Restore a matching pair, rejecting corrupt/mismatched bundles first.

        Endpoint order, cartridge hashes and hardware modes must match. If an
        endpoint rejects a state, both endpoints are restored to their previous
        state. No conversation or other application data is part of this archive.
        """
        with self._lock:
            self._require_open()
            try:
                with ZipFile(file_like_object) as archive:
                    names = archive.namelist()
                    if len(names) != 3 or set(names) != {"cable.json", "0.state", "1.state"}:
                        raise ValueError("Unexpected cable archive members")
                    if any(info.file_size > MAX_STATE_BYTES for info in archive.infolist()):
                        raise ValueError("Oversized cable state")
                    metadata = json.loads(archive.read("cable.json"))
                    states = [archive.read(f"{side}.state") for side in (0, 1)]
                self._validate_state(metadata, states)
            except (BadZipFile, KeyError, TypeError, ValueError) as error:
                raise PyBoyInvalidInputException(f"Invalid cable state: {error}") from error
            previous = [machine._link_snapshot(self._owner) for machine in self.machines]
            try:
                for side, machine in enumerate(self.machines):
                    machine._link_restore(self._owner, states[side], metadata["runtime"][side])
            except BaseException:
                for machine, (state, runtime) in zip(self.machines, previous):
                    machine._link_restore(self._owner, state, runtime)
                raise
            for field in ("cycles", "epochs", "bits", "edges", "transfers", "connected"):
                setattr(self, "_" + field, metadata[field])
            (self._halt.set if metadata["halted"] else self._halt.clear)()

    def _validate_state(self, data, states):
        if data["format"] != STATE_FORMAT or data["state_version"] != STATE_VERSION:
            raise ValueError("Unsupported cable state version")
        if data["identities"] != [list(machine._link_identity()) for machine in self.machines]:
            raise ValueError("Cartridge order or hardware modes differ")
        if len(data["runtime"]) != 2 or len(data["sha256"]) != 2:
            raise ValueError("Expected two endpoints")
        for name in ("connected", "halted"):
            if type(data[name]) is not bool:
                raise ValueError("Invalid cable flags")
        for name in ("cycles", "epochs", "bits", "edges", "transfers"):
            if len(data[name]) != 2:
                raise ValueError("Expected two cable counters")
            for value in data[name]:
                if name == "edges" and value is None:
                    continue
                _integer(value, -1 if name == "epochs" else 0)
                if name == "bits" and value > 8:
                    raise ValueError("Invalid partial byte")
        for side, state in enumerate(states):
            if not state or state[0] != STATE_VERSION or hashlib.sha256(state).hexdigest() != data["sha256"][side]:
                raise ValueError("Endpoint state checksum/version mismatch")
            runtime = data["runtime"][side]
            _integer(runtime["frame_count"], 0)
            _integer(runtime["epoch"], 0)
            if type(runtime["frame_started"]) is not bool:
                raise ValueError("Invalid frame boundary")
            for event in runtime["events"]:
                _event(event)
            for frame, event in runtime["queued_input"]:
                _integer(frame, runtime["frame_count"])
                _event(event)

    def _require_open(self):
        if self._closed:
            raise PyBoyInvalidOperationException("LinkCable is closed")

    def close(self):
        self.halt()
        with self._lock:
            if not self._closed:
                for machine in self.machines:
                    machine._link_detach(self._owner)
                self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _integer(value, minimum):
    if type(value) is not int or not minimum <= value < 2**63:
        raise ValueError("Invalid cable counter")


def _event(event):
    _integer(event, WindowEvent.PRESS_ARROW_UP)
    if event > WindowEvent.RELEASE_BUTTON_START:
        raise ValueError("Invalid joypad event")
