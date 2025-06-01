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


def test_interaction_debug_output(capsys):
    interaction = Interaction()

    # 1. Debug off - Press A
    interaction.key_event(WindowEvent.PRESS_BUTTON_A)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert interaction.standard == 0xE # P10 (A) is reset (0)

    # 2. Toggle debug on
    interaction.toggle_debug()
    assert interaction.debug is True

    # 3. Debug on - Press B
    interaction.key_event(WindowEvent.PRESS_BUTTON_B)
    captured = capsys.readouterr()
    assert "Key event: PRESS_BUTTON_B" in captured.out
    # Directional is 0xf, Standard A (0) and B (1) are reset -> 0b1100 -> 0xc
    assert f"Directional: {interaction.directional:#0x}, Standard: {interaction.standard:#0x}" in captured.out
    assert "Directional: 0xf, Standard: 0xc" in captured.out
    assert interaction.standard == 0xC

    # 4. Debug on - Release A
    interaction.key_event(WindowEvent.RELEASE_BUTTON_A)
    captured = capsys.readouterr()
    assert "Key event: RELEASE_BUTTON_A" in captured.out
    # Directional is 0xf, Standard B (1) is reset, A (0) is set -> 0b1101 -> 0xd
    assert f"Directional: {interaction.directional:#0x}, Standard: {interaction.standard:#0x}" in captured.out
    assert "Directional: 0xf, Standard: 0xd" in captured.out
    assert interaction.standard == 0xD

    # 5. Toggle debug off
    interaction.toggle_debug()
    assert interaction.debug is False

    # 6. Debug off - Press Start
    interaction.key_event(WindowEvent.PRESS_BUTTON_START)
    captured = capsys.readouterr()
    assert captured.out == ""
    # Standard B (1) and START (3) are reset -> 0b0101 -> 0x5
    assert interaction.standard == 0x5
