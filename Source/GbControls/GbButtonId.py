# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEnum import AutoEnum


class GbButtonId(AutoEnum):
    """GB Button ID enum"""

    NONE = ()           # NULL-button
    START = ()          # START-button
    SELECT = ()         # SELECT-button
    A = ()              # A-button
    B = ()              # B-button
    DPAD_LEFT = ()      # DPAD-left
    DPAD_RIGHT = ()     # DPAD-right
    DPAD_UP = ()        # DPAD-up
    DPAD_DOWN = ()      # DPAD-down
    EMU_DEBUG = ()      # Emulator debug toggle
    EMU_SPEED = ()      # Emulator speed toggle
    EMU_QUIT = ()       # Emulator quit
    EMU_LOAD = ()       # Emulator load state
    EMU_SAVE = ()       # Emulator save state

    @staticmethod
    def isButton(button):
        """Asserth whter button is a GB-button (not DPAD)"""

        if not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-intance')

        return button in (GbButtonId.START, GbButtonId.SELECT,
                GbButtonId.A, GbButtonId.B)

    @staticmethod
    def isDpad(button):
        """Assert whether button is a DPAD-member"""

        if not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-instance')

        return button in (GbButtonId.DPAD_LEFT, GbButtonId.DPAD_RIGHT,
                GbButtonId.DPAD_UP, GbButtonId.DPAD_DOWN)

    @staticmethod
    def isNone(button):
        """Assert whether button is a Nul-value"""

        if button is None:
            return True
        elif not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-instance')

        return button == NONE

    @staticmethod
    def isEmu(button):
        """Assert whether button is an Emulator-button"""

        if button is None:
            return True
        elif not isinstance(button, GbButtonId):
            raise TypeError('Did not receive a GbButtonId-instance')

        return button in (GbButtonId.EMU_DEBUG, GbButtonId.EMU_SPEED,
                GbButtonId.EMU_QUIT, GbButtonId.EMU_SAVE, GbButtonId.EMU_LOAD)
