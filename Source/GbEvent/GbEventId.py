# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEnum import AutoEnum


class GbEventId(AutoEnum):
    """GB event enum"""

    NULL_EVENT = ()     # NULL-event : do not use
    QUIT = ()           # Quit/clean exit-event
    STATE_IO = ()       # Motherboard save/load-state event
    SPEED_CHANGED = ()  # Motherboard tick-speed update event
    DEBUG_TOGGLE = ()   # Debug-mode enabled-state update event
    INPUT_UPDATE = ()   # Input update event
    FRAME_UPDATE = ()   # Frame update event
    MB_TICK = ()        # Motherboard tick event
