#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import PIL
import pytest

from pyboy import PyBoy
from pyboy.utils import PyBoyFeatureDisabledError

OVERWRITE_PNGS = False


@pytest.mark.parametrize("sampling", [True, False])
def test_swoosh(default_rom, sampling):
    sample_rate = 24000
    pyboy = PyBoy(default_rom, window="null", sound_sample_rate=sample_rate)

    frames = 60
    pointer = 0
    buffers = np.zeros((sample_rate // 60 * frames, 2))
    # array("b", [0] * (sample_rate) * 2 * (frames//60))

    for _ in range(frames):
        pyboy.tick(1, sound=sampling)
        audiobuffer = pyboy.sound.ndarray
        length, _ = audiobuffer.shape
        buffers[pointer : pointer + length] = audiobuffer[:]
        pointer += len(audiobuffer)

    left_channel = buffers[:, 0]
    right_channel = buffers[:, 1]
    time = np.linspace(0, len(left_channel) / sample_rate, num=len(left_channel))

    # Plot the channels
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(time, left_channel, label="Left Channel", color="blue")
    plt.title("Left Channel")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.ylim(-0.4, 15.4)

    plt.subplot(2, 1, 2)
    plt.plot(time, right_channel, label="Right Channel", color="red")
    plt.title("Right Channel")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.ylim(-0.4, 15.4)

    plt.tight_layout()

    png_path = Path(f"tests/test_results/sound_swoosh_{'sampling' if sampling else 'nosampling'}.png")
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        plt.savefig(png_path)
    else:
        # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
        plt_data = io.BytesIO()
        plt.savefig(plt_data, format="png")
        plt_data.seek(0)
        image = PIL.Image.open(plt_data).convert("RGB")
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image, old_image)
        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
            plt.show()
        assert not diff.getbbox(), "Images are different!"


def test_api_sound_enabled(default_rom):
    pyboy = PyBoy(default_rom, window="null", sound_emulated=True)

    pyboy.sound.raw_buffer[0]  # No exception
    pyboy.sound.raw_ndarray[0]  # No exception
    assert pyboy.sound.ndarray.shape == (0, 2), "Assumed empty sound buffer"

    for _ in range(60):
        pyboy.tick(1, False, True)  # Sampling sound
        if any(x != 0 for x in pyboy.sound.raw_buffer):
            break
    else:
        assert None, "Expected sound sampling"


def test_api_sound_disabled(default_rom):
    pyboy = PyBoy(default_rom, window="null", sound_emulated=False)

    assert pyboy.sound.raw_buffer[0] == 0  # Always defined, but empty
    assert all(x == 0 for x in pyboy.sound.raw_buffer)  # Always defined, but empty
    with pytest.raises(PyBoyFeatureDisabledError):
        pyboy.sound.raw_ndarray[0]
    with pytest.raises(PyBoyFeatureDisabledError):
        pyboy.sound.ndarray[0]

    for _ in range(60):
        pyboy.tick(1, False, True)  # Try sampling anyway
        assert all(x == 0 for x in pyboy.sound.raw_buffer)  # Always defined, but empty


@pytest.mark.parametrize("sample_rate", [3000, 6000, 12000, 24000, 44100, 48000, 88200, 96000])
def test_buffer_overrun(default_rom, capsys, sample_rate):
    pyboy = PyBoy(default_rom, window="null", sound_sample_rate=sample_rate)
    for _ in range(200):
        pyboy.tick(1, False, True)

    # Watch out for critical "Buffer overrun" log from sound
    captured = capsys.readouterr()
    assert captured.out == ""
