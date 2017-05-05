# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import EmuInput
import sdl2

class SdlInput(EmuInput):

    ARROW_UP = sdl2.SDLK_UP
    ARROW_DOWN = sdl2.SDLK_DOWN
    ARROW_RIGHT = sdl2.SDLK_RIGHT
    ARROW_LEFT = sdl2.SDLK_LEFT
    BUTTON_A = sdl2.SDLK_a
    BUTTON_S = sdl2.SDLK_s
    BUTTON_D = sdl2.SDLK_d
    BUTTON_E = sdl2.SDLK_e
    BUTTON_Z = sdl2.SDLK_z
    BUTTON_X = sdl2.SDLK_x
    RETURN = sdl2.SDLK_RETURN
    BACKSPACE = sdl2.SDLK_BACKSPACE
    ESCAPE = sdl2.SDLK_ESCAPE
    SPACE = sdl2.SDLK_SPACE

