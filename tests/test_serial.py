#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_serial_transfer_clears_busy_flag(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, False)

    # Start a transfer using the internal clock. Bit 7 (transfer in
    # progress) reads back as set until the transfer completes.
    pyboy.memory[0xFF02] = 0x81
    assert pyboy.memory[0xFF02] & 0x80

    # 8 bits at 8192Hz take about 1ms -- well within one frame. Games
    # poll bit 7 to detect completion, so it has to read back as cleared.
    pyboy.tick(1, False)
    assert not pyboy.memory[0xFF02] & 0x80

    # Disconnected link cable always reads 0xFF
    assert pyboy.memory[0xFF01] == 0xFF

    pyboy.stop(save=False)
