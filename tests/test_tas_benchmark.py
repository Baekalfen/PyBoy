import base64
import hashlib
import json
import zlib

import pytest

from tools import benchmark_tas
from tools.benchmark_tas import discover_replays, load_replay, play_replay
from pyboy.utils import WindowEvent


def _write_replay(rom_path, replay_path, events, state=None):
    rom_hash = base64.b64encode(hashlib.sha256(rom_path.read_bytes()).digest()).decode("ascii")
    encoded_state = None if state is None else base64.b64encode(state).decode("ascii")
    payload = json.dumps((events, rom_hash, encoded_state)).encode("ascii")
    replay_path.write_bytes(zlib.compress(payload))


def test_load_replay_validates_hash_and_extracts_frames(tmp_path):
    rom_path = tmp_path / "game.gb"
    replay_path = tmp_path / "game.gb.replay"
    rom_path.write_bytes(b"test rom")
    events = [[0, [1], ""], [3, [2, 3], ""]]
    _write_replay(rom_path, replay_path, events, b"state")

    loaded_events, state, frame_count = load_replay(rom_path, replay_path)

    assert loaded_events == events
    assert state == b"state"
    assert frame_count == 4

    rom_path.write_bytes(b"different rom")
    with pytest.raises(ValueError, match="hash does not match"):
        load_replay(rom_path, replay_path)


def test_load_replay_rejects_unordered_events(tmp_path):
    rom_path = tmp_path / "game.gb"
    replay_path = tmp_path / "game.gb.replay"
    rom_path.write_bytes(b"test rom")
    _write_replay(rom_path, replay_path, [[3, [1], ""], [2, [2], ""]])

    with pytest.raises(ValueError, match="unordered frame"):
        load_replay(rom_path, replay_path)


def test_discover_replays_requires_adjacent_rom(tmp_path):
    rom_path = tmp_path / "game.gb"
    replay_path = tmp_path / "game.gb.replay"
    orphan_replay = tmp_path / "orphan.gb.replay"
    rom_path.write_bytes(b"test rom")
    replay_path.write_bytes(b"")
    orphan_replay.write_bytes(b"")

    assert discover_replays(tmp_path) == [replay_path]


def test_play_replay_applies_inputs_at_recorded_frames():
    class FakePyBoy:
        def __init__(self):
            self.events = []

        def send_input(self, event):
            self.events.append(("input", event))

        def tick(self, frames, render, sound):
            self.events.append(("tick", frames, render, sound))
            return True

    pyboy = FakePyBoy()
    play_replay(pyboy, [[0, [10, 11], ""], [2, [12], ""]], 3, 1)

    assert pyboy.events == [
        ("input", 10),
        ("input", 11),
        ("tick", 1, True, False),
        ("tick", 1, True, False),
        ("input", 12),
        ("tick", 1, True, False),
    ]


def test_play_replay_batches_ticks_without_moving_inputs():
    class FakePyBoy:
        def __init__(self):
            self.events = []

        def send_input(self, event):
            self.events.append(("input", event))

        def tick(self, frames, render, sound):
            self.events.append(("tick", frames, render, sound))
            return True

    pyboy = FakePyBoy()
    play_replay(pyboy, [[0, [10], ""], [3, [11], ""], [7, [12], ""]], 9, 4)

    assert pyboy.events == [
        ("input", 10),
        ("tick", 3, False, False),
        ("input", 11),
        ("tick", 1, True, False),
        ("tick", 3, False, False),
        ("input", 12),
        ("tick", 1, True, False),
        ("tick", 1, True, False),
    ]


def test_play_replay_rejects_nonpositive_render_interval():
    with pytest.raises(ValueError, match="render_every must be positive"):
        play_replay(None, [], 1, 0)


def test_play_replay_filters_recorder_control_events():
    class FakePyBoy:
        def __init__(self):
            self.events = []

        def send_input(self, event):
            self.events.append(event)

        def tick(self, frames, render, sound):
            return True

    pyboy = FakePyBoy()
    play_replay(
        pyboy,
        [[0, [WindowEvent.SCREEN_RECORDING_TOGGLE, 10], ""]],
        1,
        None,
    )

    assert pyboy.events == [10]


def test_benchmark_replay_uses_requested_bootrom(monkeypatch, tmp_path):
    constructor = {}

    class FakePyBoy:
        def __init__(self, rom_path, **kwargs):
            constructor["rom_path"] = rom_path
            constructor.update(kwargs)

        def set_emulation_speed(self, speed):
            pass

        def save_state(self, file):
            file.write(b"state")

        def load_state(self, file):
            pass

        def tick(self, frames, render, sound):
            return True

        def stop(self, save):
            pass

    monkeypatch.setattr(benchmark_tas, "PyBoy", FakePyBoy)
    bootrom = tmp_path / "cgb_boot.bin"
    bootrom.write_bytes(b"bootrom")

    result = benchmark_tas.benchmark_replay(
        "game.gbc",
        [],
        None,
        1,
        1,
        1,
        False,
        None,
        bootrom,
    )

    assert constructor["bootrom"] == bootrom
    assert result["bootrom"] == str(bootrom)
