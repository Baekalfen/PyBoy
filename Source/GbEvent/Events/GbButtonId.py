# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEnum import AutoEnum


class GbButtonId(AutoEnum):
    """GB Button ID enum"""
    NONE = 0            # NULL-button
    START = ()          # START-button
    SELECT = ()         # SELECT-button
    A = ()              # A-button
    B = ()              # B-button
    DPAD_LEFT = ()      # DPAD-left
    DPAD_RIGHT = ()     # DPAD-right
    DPAD_UP = ()        # DPAD-up
    DPAD_DOWN = ()      # DPAD-down

    @staticmethod
    def isButton(button):
        """Asserth whter button is a GB-button (not DPAD)"""

        if not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-intance')

        return button in (START, SELECT, A, B)

    @staticmethod
    def isDpad(button):
        """Assert whether button is a DPAD-member"""

        if not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-instance')

        return button in (DPAD_LEFT, DPAD_RIGHT, DPAD_UP, DPAD_DOWN)

    @staticmethod
    def isNone(button):
        """Assert whether button is a Nul-value"""

        if button is None:
            return True
        elif not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-instance')

        return button == NONE
