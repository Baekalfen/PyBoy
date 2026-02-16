#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

from pyboy import PyBoy
from pyboy.utils import WindowEvent
from pyboy.pyboy import DMG_PALETTES


def test_cycle_palette_changes_and_wraps(default_rom):
    """Test that cycling changes the screen and wrapping returns to original."""
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, True, False)

    # Capture the initial screen
    screen_initial = pyboy.screen.ndarray.copy()

    # Cycling once should change the screen
    pyboy._cycle_palette()
    pyboy.tick(1, True, False)
    screen_after_one = pyboy.screen.ndarray.copy()
    assert not np.array_equal(screen_initial, screen_after_one)

    # Cycling through the remaining palettes should wrap back to the original
    for _ in range(len(DMG_PALETTES) - 1):
        pyboy._cycle_palette()
    pyboy.tick(1, True, False)
    screen_wrapped = pyboy.screen.ndarray.copy()
    assert np.array_equal(screen_initial, screen_wrapped)

    pyboy.stop(save=False)


def test_cycle_palette_event(default_rom):
    """Test that the CYCLE_PALETTE WindowEvent triggers a palette change."""
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, True, False)

    screen_before = pyboy.screen.ndarray.copy()

    pyboy.send_input(WindowEvent.CYCLE_PALETTE)
    pyboy.tick(1, True, False)

    screen_after = pyboy.screen.ndarray.copy()
    assert not np.array_equal(screen_before, screen_after)

    pyboy.stop(save=False)


def test_cycle_palette_ignored_in_cgb(any_rom_cgb):
    """Test that palette cycling is a no-op in CGB mode."""
    pyboy = PyBoy(any_rom_cgb, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, True, False)

    screen_before = pyboy.screen.ndarray.copy()

    pyboy._cycle_palette()
    pyboy.tick(1, True, False)

    screen_after = pyboy.screen.ndarray.copy()
    assert np.array_equal(screen_before, screen_after)

    pyboy.stop(save=False)
