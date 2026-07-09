#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import builtins
from pathlib import Path

from PIL import Image, ImageSequence
import pytest

from pyboy import PyBoy
from pyboy.utils import WindowEvent


def _trace(msg):
    print(f"[screen-recorder-test] {msg}", flush=True)


def _make_pyboy(monkeypatch, tmp_path, default_rom, sample_rate=24000):
    repo_root = Path(__file__).resolve().parents[1]
    rom_path = str((repo_root / default_rom).resolve())
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("pyboy.plugins.screen_recorder.shutil.which", lambda _: "/usr/bin/ffmpeg")
    pyboy = PyBoy(rom_path, window="null", sound_emulated=True, sound_sample_rate=sample_rate)
    pyboy.set_emulation_speed(0)
    return pyboy


def test_screen_recorder_gif_pillow_pipeline(monkeypatch, tmp_path, default_rom):
    _trace("Starting GIF recorder flow")
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom)
    ffmpeg_calls = []

    def _fake_subprocess_run(cmd, stdout=None, stderr=None, check=None):
        ffmpeg_calls.append(cmd)
        return type("P", (), {"returncode": 0, "stderr": b""})()

    monkeypatch.setattr("pyboy.plugins.screen_recorder.subprocess.run", _fake_subprocess_run)

    _trace("Toggle ON GIF recording")
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(2, True, True)
    _trace("Toggle OFF GIF recording")
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    _trace(f"Captured {len(ffmpeg_calls)} ffmpeg calls for GIF")
    assert ffmpeg_calls == []

    gif_files = list((tmp_path / "recordings").glob("*.gif"))
    assert len(gif_files) == 1

    with Image.open(gif_files[0]) as gif:
        frames = list(ImageSequence.Iterator(gif))
        assert gif.format == "GIF"
        assert len(frames) >= 1
        assert frames[0].size == pyboy.screen.image.size
    assert list((tmp_path / "recordings").glob("screenrec-*")) == []

    pyboy.stop(save=False)
    _trace("GIF recorder flow finished")


def test_screen_recorder_does_not_overwrite_existing_recording(monkeypatch, tmp_path, default_rom):
    monkeypatch.setattr("pyboy.plugins.screen_recorder.time.strftime", lambda _: "same-timestamp")
    pyboys = [_make_pyboy(monkeypatch, tmp_path, default_rom) for _ in range(2)]

    for pyboy in pyboys:
        pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
        pyboy.tick(1, True, True)

    for pyboy in pyboys:
        pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
        pyboy.tick(1, True, True)

    recordings = sorted(path.name for path in (tmp_path / "recordings").glob("*.gif"))
    assert recordings == ["same-timestamp-1.gif", "same-timestamp.gif"]

    for pyboy in pyboys:
        pyboy.stop(save=False)


def test_screen_recorder_hides_reserved_output_until_save(monkeypatch, tmp_path, default_rom):
    monkeypatch.setattr("pyboy.plugins.screen_recorder.time.strftime", lambda _: "same-timestamp")
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    recordings_dir = tmp_path / "recordings"
    assert list(recordings_dir.glob("*.gif")) == []
    assert list(recordings_dir.glob(".*.lock")) == [recordings_dir / ".same-timestamp.gif.lock"]

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    assert list(recordings_dir.glob("*.gif")) == [recordings_dir / "same-timestamp.gif"]
    assert list(recordings_dir.glob(".*.lock")) == []
    pyboy.stop(save=False)


def test_screen_recorder_does_not_overwrite_existing_saved_recording(monkeypatch, tmp_path, default_rom):
    monkeypatch.setattr("pyboy.plugins.screen_recorder.time.strftime", lambda _: "same-timestamp")
    recordings_dir = tmp_path / "recordings"
    recordings_dir.mkdir()
    original_gif = recordings_dir / "same-timestamp.gif"
    original_gif.write_bytes(b"original-recording")

    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    recordings = sorted(path.name for path in recordings_dir.glob("*.gif"))
    assert recordings == ["same-timestamp-1.gif", "same-timestamp.gif"]
    assert original_gif.read_bytes() == b"original-recording"

    pyboy.stop(save=False)


def test_screen_recorder_cleans_up_reserved_output_on_start_failure(monkeypatch, tmp_path, default_rom):
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom, sample_rate=48000)
    real_open = builtins.open

    def _failing_open(path, mode="r", *args, **kwargs):
        if path.endswith("audio.s8") and "w" in mode:
            raise OSError("disk full")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _failing_open)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
    with pytest.raises(OSError, match="disk full"):
        pyboy.tick(1, True, True)

    recordings_dir = tmp_path / "recordings"
    screen_recorder = pyboy._plugin_manager.screen_recorder
    assert list(recordings_dir.glob("*.mp4")) == []
    assert list(recordings_dir.glob(".*.lock")) == []
    assert list(recordings_dir.glob("screenrec-*")) == []
    assert screen_recorder._session is None
    assert not screen_recorder.recording_gif
    assert not screen_recorder.recording_mp4

    def _fake_subprocess_run(cmd, stdout=None, stderr=None, check=None):
        Path(cmd[-1]).write_bytes(b"mp4")
        return type("P", (), {"returncode": 0, "stderr": b""})()

    monkeypatch.setattr("builtins.open", real_open)
    monkeypatch.setattr("pyboy.plugins.screen_recorder.subprocess.run", _fake_subprocess_run)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
    pyboy.tick(1, True, True)
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
    pyboy.tick(1, True, True)

    retry_recordings = list(recordings_dir.glob("*.mp4"))
    assert len(retry_recordings) == 1
    assert list(recordings_dir.glob(".*.lock")) == []
    pyboy.stop(save=False)


def test_screen_recorder_cleans_up_tempdir_on_reservation_failure(monkeypatch, tmp_path, default_rom):
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom)
    real_reserve_output_path = pyboy._plugin_manager.screen_recorder.__class__._reserve_output_path

    def _failing_reservation(*args, **kwargs):
        raise OSError("read-only filesystem")

    monkeypatch.setattr("pyboy.plugins.screen_recorder.ScreenRecorder._reserve_output_path", _failing_reservation)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    with pytest.raises(OSError, match="read-only filesystem"):
        pyboy.tick(1, True, True)

    recordings_dir = tmp_path / "recordings"
    screen_recorder = pyboy._plugin_manager.screen_recorder
    assert list(recordings_dir.glob(".*.lock")) == []
    assert list(recordings_dir.glob("screenrec-*")) == []
    assert screen_recorder._session is None
    assert not screen_recorder.recording_gif
    assert not screen_recorder.recording_mp4

    monkeypatch.setattr(
        "pyboy.plugins.screen_recorder.ScreenRecorder._reserve_output_path", staticmethod(real_reserve_output_path)
    )

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    retry_recordings = list(recordings_dir.glob("*.gif"))
    assert len(retry_recordings) == 1
    assert list(recordings_dir.glob(".*.lock")) == []
    pyboy.stop(save=False)


def test_screen_recorder_removes_partial_output_when_encoding_fails(monkeypatch, tmp_path, default_rom):
    monkeypatch.setattr("pyboy.plugins.screen_recorder.time.strftime", lambda _: "same-timestamp")
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom)

    def _failing_encode(self, session):
        Path(session["output_path"]).write_bytes(b"partial-gif")
        return False

    monkeypatch.setattr("pyboy.plugins.screen_recorder.ScreenRecorder._encode_gif", _failing_encode)

    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    pyboy.tick(1, True, True)

    recordings_dir = tmp_path / "recordings"
    assert list(recordings_dir.glob("*.gif")) == []
    assert list(recordings_dir.glob(".*.lock")) == []
    assert list(recordings_dir.glob("screenrec-*")) == []
    pyboy.stop(save=False)


def test_screen_recorder_mp4_does_not_overwrite_existing_recording(monkeypatch, tmp_path, default_rom):
    monkeypatch.setattr("pyboy.plugins.screen_recorder.time.strftime", lambda _: "same-timestamp")
    pyboys = [_make_pyboy(monkeypatch, tmp_path, default_rom, sample_rate=48000) for _ in range(2)]

    def _fake_subprocess_run(cmd, stdout=None, stderr=None, check=None):
        Path(cmd[-1]).write_bytes(b"mp4")
        return type("P", (), {"returncode": 0, "stderr": b""})()

    monkeypatch.setattr("pyboy.plugins.screen_recorder.subprocess.run", _fake_subprocess_run)

    for pyboy in pyboys:
        pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
        pyboy.tick(1, True, True)

    for pyboy in pyboys:
        pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
        pyboy.tick(1, True, True)

    recordings_dir = tmp_path / "recordings"
    recordings = sorted(path.name for path in recordings_dir.glob("*.mp4"))
    assert recordings == ["same-timestamp-1.mp4", "same-timestamp.mp4"]
    assert list(recordings_dir.glob(".*.lock")) == []
    assert list(recordings_dir.glob("screenrec-*")) == []

    for pyboy in pyboys:
        pyboy.stop(save=False)


def test_screen_recorder_mp4_with_audio(monkeypatch, tmp_path, default_rom):
    _trace("Starting MP4 recorder flow")
    pyboy = _make_pyboy(monkeypatch, tmp_path, default_rom, sample_rate=48000)
    ffmpeg_calls = []

    def _fake_subprocess_run(cmd, stdout=None, stderr=None, check=None):
        ffmpeg_calls.append(cmd)
        return type("P", (), {"returncode": 0, "stderr": b""})()

    monkeypatch.setattr("pyboy.plugins.screen_recorder.subprocess.run", _fake_subprocess_run)

    _trace("Toggle ON MP4 recording")
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
    pyboy.tick(2, True, True)
    _trace("Toggle OFF MP4 recording")
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4)
    pyboy.tick(1, True, True)

    _trace(f"Captured {len(ffmpeg_calls)} ffmpeg calls for MP4")
    assert len(ffmpeg_calls) == 1
    cmd = ffmpeg_calls[0]
    _trace(f"MP4 call args: {cmd}")
    assert "libx264" in cmd
    assert "aac" in cmd
    assert "s8" in cmd
    assert "48000" in cmd
    pyboy.stop(save=False)
    _trace("MP4 recorder flow finished")
