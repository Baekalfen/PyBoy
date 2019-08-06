#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import hashlib
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

def test_screen_buffer_and_image():
    for window, boot_logo_hash_predigested in [
            # These are different because the underlying format is different. We'll test the actual image afterwards.
            ("SDL2", b'=\xff\xf9z 6\xf0\xe9\xcb\x05J`PM5\xd4rX+\x1b~z\xef1\xe0\x82\xc4t\x06\x82\x12C'),
            ("OpenGL", b's\xd1R\x88\xe0a\x14\xd0\xd2\xecOk\xe8b\xae.\x0e\x1e\xb6R\xc2\xe9:\xa2\x0f\xae\xa2\x89M\xbf\xd8|')
            ]:
        pyboy = PyBoy(window, 1, any_rom, boot_rom)
        pyboy.set_emulation_speed(False)
        for n in range(275): # Iterate to boot logo
            pyboy.tick()

        boot_logo_hash = hashlib.sha256()
        boot_logo_hash.update(pyboy.get_raw_screen_buffer())
        assert boot_logo_hash.digest() == boot_logo_hash_predigested

        # The output of `get_screen_image` is supposed to be homogeneous, which means a shared hash between versions.
        boot_logo_png_hash_predigested = (
                b'\xf4b,(\xbe\xaa\xf8\xec\x06\x9fJ-\x84\xd3I\x16\xb8'
                b'\xe3\xd0\xd5\xae\x80\x01\x1e\x96\xba!1\xeb\xd1\xce_'
            )
        boot_logo_png_hash = hashlib.sha256()
        image = pyboy.get_screen_image()
        image_data = io.BytesIO()
        image.save(image_data, format='BMP')
        boot_logo_png_hash.update(image_data.getvalue())
        assert boot_logo_png_hash.digest() == boot_logo_png_hash_predigested

        # get_raw_screen_buffer_as_nparray
        numpy_hash = hashlib.sha256()
        numpy_array = np.ascontiguousarray(pyboy.get_raw_screen_buffer_as_nparray())
        assert numpy_array.shape == (144, 160, 3)
        numpy_hash.update(numpy_array.tobytes())
        assert numpy_hash.digest() == (
                b'\r\t\x87\x131\xe8\x06\x82\xcaO=\n\x1e\xa2K$'
                b'\xd6\x8e\x91R( H7\xd8a*B+\xc7\x1f\x19'
            )

        pyboy.stop(save=False)


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

