# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from enum import Enum

class AutoEnum(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class WindowEvent(AutoEnum):
    __order__ = "Quit PressArrowUp PressArrowDown PressArrowRight\
    PressArrowLeft\
    PressButtonA PressButtonB PressButtonSelect PressButtonStart\
    ReleaseArrowUp\
    ReleaseArrowDown ReleaseArrowRight ReleaseArrowLeft ReleaseButtonA\
    ReleaseButtonB ReleaseButtonSelect ReleaseButtonStart DebugToggle\
    PressSpeedUp ReleaseSpeedUp SaveState LoadState"

    Quit = ()
    PressArrowUp = ()
    PressArrowDown = ()
    PressArrowRight = ()
    PressArrowLeft = ()
    PressButtonA = ()
    PressButtonB = ()
    PressButtonSelect = ()
    PressButtonStart = ()
    ReleaseArrowUp = ()
    ReleaseArrowDown = ()
    ReleaseArrowRight = ()
    ReleaseArrowLeft = ()
    ReleaseButtonA = ()
    ReleaseButtonB = ()
    ReleaseButtonSelect = ()
    ReleaseButtonStart = ()
    DebugToggle = ()
    PressSpeedUp = ()
    ReleaseSpeedUp = ()
    SaveState = ()
    LoadState = ()
