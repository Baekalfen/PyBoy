# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEnum import AutoEnum


class GbButtonState(AutoEnum):
    """GB buttom state enum"""

    PRESSED = ()   # Button pressed
    RELEASED = ()  # Button released


