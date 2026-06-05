#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pathlib import Path

from PIL import Image, ImageSequence

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
