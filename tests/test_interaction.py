#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest
from pyboy import PyBoy
from pyboy.core.interaction import Interaction
from pyboy.utils import cython_compiled, WindowEvent


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_pull():
    interaction = Interaction()

    # Zero selects!
    dpad = 0b10 << 4
    buttons = 0b01 << 4

    assert interaction.pull(dpad) == 0b11001111
    assert interaction.pull(buttons) == 0b11001111
    assert interaction.pull(buttons | dpad) == 0b11001111
    # TODO: Undefined?
    # assert interaction.pull(0xFF)

    interaction.key_event(WindowEvent.PRESS_ARROW_RIGHT)
    assert interaction.pull(dpad) == 0b11001110
    assert interaction.pull(buttons) == 0b11001111
    assert interaction.pull(buttons | dpad) == 0b11001111

    interaction.key_event(WindowEvent.RELEASE_ARROW_RIGHT)
    assert interaction.pull(dpad) == 0b11001111
    assert interaction.pull(buttons) == 0b11001111
    assert interaction.pull(buttons | dpad) == 0b11001111

    interaction.key_event(WindowEvent.PRESS_BUTTON_B)
    assert interaction.pull(dpad) == 0b11001111
    assert interaction.pull(buttons) == 0b11001101
    assert interaction.pull(buttons | dpad) == 0b11001111

    interaction.key_event(WindowEvent.RELEASE_BUTTON_B)
    assert interaction.pull(dpad) == 0b11001111
    assert interaction.pull(buttons) == 0b11001111
    assert interaction.pull(buttons | dpad) == 0b11001111


def test_button(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000  # Select d-pad (bit-4 low)
    assert pyboy.memory[0xFF00] == 0b1100_1111  # High means released

    pyboy.button("down")
    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000
    assert pyboy.memory[0xFF00] == 0b1100_0111  # down pressed
    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000
    assert pyboy.memory[0xFF00] == 0b1100_1111  # auto-reset

    pyboy.button("down")
    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000
    assert pyboy.memory[0xFF00] == 0b1100_0111  # down pressed
    pyboy.button("down")
    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000
    assert pyboy.memory[0xFF00] == 0b1100_0111  # down is kept pressed
    pyboy.tick(1, False, False)
    pyboy.memory[0xFF00] = 0b0010_0000
    assert pyboy.memory[0xFF00] == 0b1100_1111  # auto-reset
