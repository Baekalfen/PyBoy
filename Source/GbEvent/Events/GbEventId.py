# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEnum import AutoEnum


class GbEventId(AutoEnum):
    NULL_EVENT = 0
    QUIT = ()
    STATE_IO = ()
    SPEED_CHANGED = ()
    DEBUG_TOGGLE = ()
    INPUT_UPDATE = ()
