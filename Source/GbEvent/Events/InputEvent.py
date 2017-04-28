# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId
from . import GbButtonId, GbButtonState

from MathUint8 import  resetBit, setBit

        # Bit 7 - Not used (No$GMB)
        # Bit 6 - Not used (No$GMB)
        # Bit 5 - P15 out port
        # Bit 4 - P14 out port
        # Bit 3 - P13 in port
        # Bit 2 - P12 in port
        # Bit 1 - P11 in port
        # Bit 0 - P10 in port

P10, P11, P12, P13, P14, P15 = range(0,6)


REG_DPAD_RIGHT_OFFSET = P10
REG_DPAD_LEFT_OFFSET = P11
REG_DPAD_UP_OFFSET = P12
REG_DPAD_DOWN_OFFSET = P13

REG_BUTTON_SELECT_OFFSET = P12
REG_BUTTON_START_OFFSET = P13
REG_BUTTON_A_OFFSET = P10
REG_BUTTON_B_OFFSET = P11


class InputEvent(GbEvent):

    _ID = GbEventId.INPUT_UPDATE

    def __init__(self, system, eventHandler, buttons, state):
        super(self.__class__, self).__init__(system, eventHandler)
        self._buttons = buttons
        self._state = state

    def do_call(self):

        ref_offset = 0

        for button in self._buttons:
            self.updateButton(button)

    def updateButton(self, button):
        if button == GbButtonId.DPAD_RIGHT:
            reg_offset = REG_DPAD_RIGHT_OFFSET
        elif button == GbButtonId.DPAD_LEFT:
            reg_offset = REG_DPAD_LEFT_OFFSET_OFFSET
        elif button == GbButtonId.DPAD_UP:
            reg_offset = REG_DPAD_UP_OFFSET
        elif button == GbButtonId.DPAD_DOWN:
            reg_offset = REG_DPAD_DOWN_OFFSET
        elif button == GbButtonId.A:
            reg_offset = REG_BUTTON_A_OFFSET
        elif button == GbButtonId.B:
            reg_offset = REG_BUTTON_B_OFFSET
        elif button == GbButtonId.SELECT:
            reg_offset = REG_BUTTON_SELECT_OFFSET
        elif button == GbButtonId.START:
            reg_offset = REG_BUTTON_START_OFFSET
        else:
            raise RuntimeError('Unrecognized button ID: {}'.format(button))

        if GbButtonId.isDpad(button):
            if self._state == GbButtonState.PRESSED:
                system.dpadControl = setBit(system.dpadControl, ref_offset)
            elif self._state == GbButtonState.RELEASED:
                system.dpadControl = resetBit(system.dpadControl, ref_offset)
        else:
            if self._state == GbButtonState.PRESSED:
                system.buttonControl = setBit(system.buttonControl, ref_offset)
            elif self._state == GbButtonState.RELEASED:
                system.buttonControl = resetBit(system.buttonControl, ref_offset)

