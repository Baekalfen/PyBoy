# -*- encoding: utf-8 -*-
#
# Authors: Thoams Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

# from .. import Global

from AbstractGameWindow import AbstractGameWindow
from GameWindow_dummy import DummyGameWindow

# if Global.isPyPy:
from GameWindow_SDL2 import SdlGameWindow
# else:
#     from .GameWindow_PyGame import PyGameGameWindow


