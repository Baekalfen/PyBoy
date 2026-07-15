#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
from pyboy.utils import PyBoyException
import pytest

from pyboy import PyBoy


def make_rtc_rom():
    # Minimal MBC3+TIMER+RAM+BATTERY cartridge (0x10), 32KB RAM.
    rom = bytearray(2 * 16 * 1024)
    rom[0x0134:0x013C] = b"RTC TEST"
    rom[0x0147] = 0x10
    rom[0x0149] = 0x03
    checksum = 0
    for m in range(0x0134, 0x014D):
        checksum = (checksum - rom[m] - 1) & 0xFF
    rom[0x014D] = checksum
    return io.BytesIO(bytes(rom))


def _latch(pyboy):
    pyboy.memory[0x6000] = 0x00
    pyboy.memory[0x6000] = 0x01


def _read_rtc_register(pyboy, register):
    pyboy.memory[0x4000] = register
    return pyboy.memory[0xA000]


def test_rtc_tracks_writes_when_unlocked():
    pyboy = PyBoy(make_rtc_rom(), window="null")
    pyboy.memory[0x0000] = 0x0A  # enable RAM/RTC access

    # Set the seconds register to 30, then latch and read it back.
    pyboy.memory[0x4000] = 0x08
    _latch(pyboy)
    pyboy.memory[0xA000] = 30
    _latch(pyboy)
    # Allow one second of host-clock skew between write and read.
    assert _read_rtc_register(pyboy, 0x08) in (30, 31)

    pyboy.stop(save=False)


def test_rtc_lock_freezes_clock():
    pyboy = PyBoy(make_rtc_rom(), window="null")
    pyboy.rtc_lock_experimental(True)
    pyboy.memory[0x0000] = 0x0A

    _latch(pyboy)
    for register in (0x08, 0x09, 0x0A, 0x0B):  # sec, min, hour, day
        assert _read_rtc_register(pyboy, register) == 0

    # Even after the game sets the clock, a locked RTC keeps reading the
    # same frozen value — this is what makes emulation reproducible.
    pyboy.memory[0x4000] = 0x08
    pyboy.memory[0xA000] = 30
    _latch(pyboy)
    assert _read_rtc_register(pyboy, 0x08) == 0

    pyboy.stop(save=False)


def test_rtc_lock_accepted_without_rtc_cartridge(default_rom):
    # No RTC on the cartridge raises exception
    pyboy = PyBoy(default_rom, window="null")
    with pytest.raises(PyBoyException):
        pyboy.rtc_lock_experimental(True)
    pyboy.stop(save=False)
