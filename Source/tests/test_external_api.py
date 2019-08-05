#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
from PIL import Image

import sys
sys.path.append("..") # Adds higher directory to python modules path.

from pyboy import PyBoy

boot_rom = "../ROMs/DMG_ROM.bin"
any_rom = 'BlarggROMs/cpu_instrs/cpu_instrs.gb'

def test_misc():
    pyboy = PyBoy("dummy", 1, any_rom, boot_rom)
    pyboy.tick()
    pyboy.stop(save=False)

def test_get_screen_buffer():
    pyboy = PyBoy("SDL2", 1, any_rom, boot_rom)
    pyboy.set_emulation_speed(False)
    for n in range(275):
        pyboy.tick()

    breakpoint()
    Image.frombytes(pyboy.get_screen_buffer_format(), (160,144), pyboy.get_screen_buffer())
    pyboy.stop(save=False)

def test_get_screen_buffer_format():
    pass

def test_get_memory_value():
    pass

def test_set_memory_value():
    pass

def test_send_input():
    pass

def test_get_tile():
    pass

def test_get_sprite():
    pass

def test_get_tile_view():
    pass

def test_get_screen_position():
    pass

def test_save_state():
    pass

def test_load_state():
    pass

def test_get_serial():
    pass

def test_disable_title():
    pyboy = PyBoy("dummy", 1, any_rom, boot_rom)
    pyboy.disable_title()
    pyboy.tick()
    pyboy.stop(save=False)

def test_set_emulation_speed():
    pass

