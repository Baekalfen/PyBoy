# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from enum import Enum


class GbButtonId(Enum):
    """GB Button ID enum"""

    DPAD_MASK   = 0x0100
    BUTTON_MASK = 0x0200
    EMU_MASK    = 0x0400

    NONE           = 0                   # NULL-button
    START          = BUTTON_MASK | 0x01  # START-button
    SELECT         = BUTTON_MASK | 0x02  # SELECT-button
    A              = BUTTON_MASK | 0x03  # A-button
    B              = BUTTON_MASK | 0x04  # B-button
    DPAD_LEFT      = DPAD_MASK | 0x01    # DPAD-left
    DPAD_RIGHT     = DPAD_MASK | 0x02    # DPAD-right
    DPAD_UP        = DPAD_MASK | 0x03    # DPAD-up
    DPAD_DOWN      = DPAD_MASK | 0x04    # DPAD-down
    EMU_DEBUG      = EMU_MASK | 0x01     # Emulator debug toggle
    EMU_SPEED      = EMU_MASK | 0x02     # Emulator speed toggle
    EMU_QUIT       = EMU_MASK | 0x03     # Emulator quit
    EMU_LOAD       = EMU_MASK | 0x04     # Emulator load state
    EMU_SAVE       = EMU_MASK | 0x05     # Emulator save state
    EMU_RUN_SCRIPT = EMU_MASK | 0x06     # Run script

    def __and__(self, other):
        """AND-operator

        :param other: Second term
        """

        if isinstance(other, GbButtonId):
            return self.value & other.value
        elif isinstance(other, int):
            return self.value & other
        else:
            raise TypeError('Did not receive a gbbuttonid or int-instance')

    def __or__(self, other):
        """OR-operator

        :param other: Second term
        """
        if isinstance(other, GbButtonId):
            return self.value | other.value
        elif isinstance(other, int):
            return self.value | other
        else:
            raise TypeError('Did not receive a gbbuttonid or int-instance')

    @staticmethod
    def isButton(button):
        """Asserth whter button is a GB-button (not DPAD)"""

        if not isinstance(button, GbButtonId) and not isinstance(button, int):
            raise TypeError('Did not receive a GbButtonId or int-instance')

        return (button & GbButtonId.BUTTON_MASK) > 0

    @staticmethod
    def isDpad(button):
        """Assert whether button is a DPAD-member"""

        if not isinstance(button, GbButtonId) and not isinstance(button, int):
            raise TypeError('Did not receive a GbButtonId or int-instance')

        return (button & GbButtonId.DPAD_MASK) > 0

    @staticmethod
    def isNone(button):
        """Assert whether button is a Nul-value"""

        if button is None:
            return True
        if not isinstance(button, GbButtonId) and not isinstance(button, int):
            raise TypeError('Did not receive a GbButtonId or int-instance')

        return button == GbButtonId.NONE

    @staticmethod
    def isEmu(button):
        """Assert whether button is an Emulator-button"""

        if button is None:
            return True
        if not isinstance(button, GbButtonId) and not isinstance(button, int):
            raise TypeError('Did not receive a GbButtonId or int-instance')

        return (button & GbButtonId.EMU_MASK) > 0
