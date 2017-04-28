# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId
from . import GbButtonId, GbButtonState

from GbLogger import gblogger

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
    """Event for handling user input"""

    _ID = GbEventId.INPUT_UPDATE

    def __init__(self, system, eventHandler, mb, buttons):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param mb: Motherboard-object
        :param buttons: List of button-actions
        """
        super(self.__class__, self).__init__(system, eventHandler)
        self._buttons = buttons
        self._system = system
        self._mb = mb

    def do_call(self):
        """Event callback"""

        ref_offset = 0

        for button, state in self._buttons:
            self._updateButton(button, state)

    def _updateButton(self, button, state):
        """Update Motherboard with button state

        :param button:
        :param state: Button state
        """

        if False:
            gblogger.debug('Input update: [{}][{}]'.format(str(button),
                str(state)))

        if GbButtonId.isEmu(button):
            return self.__handleEmuButton(button, state)
        else:
            self.__handleGbButtons(button, state)

    def __handleGbButtons(self, button, state):
        """Handle GB buttons

        :param button:
        :param state: Button state
        """

        if button == GbButtonId.DPAD_RIGHT:
            reg_offset = REG_DPAD_RIGHT_OFFSET
        elif button == GbButtonId.DPAD_LEFT:
            reg_offset = REG_DPAD_LEFT_OFFSET
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
            # Signal MB that an input has updated
            self._mb.buttonEvent(button, state)

            # Resolve register
            if state == GbButtonState.PRESSED:
                self._system.dpadControl = resetBit(self._system.dpadControl, reg_offset)

            elif state == GbButtonState.RELEASED:
                self._system.dpadControl = setBit(self._system.dpadControl, reg_offset)

        elif GbButtonId.isButton(button):
            # Signal MB that an input has updated
            self._mb.buttonEvent(button, state)

            # Resolve register
            if state == GbButtonState.PRESSED:
                self._system.buttonControl = resetBit(self._system.buttonControl, reg_offset)
            elif state == GbButtonState.RELEASED:
                self._system.buttonControl = setBit(self._system.buttonControl, reg_offset)
        else:
            pass

    def __handleEmuButton(self, button, state):
        """Handle EMU buttons

        :param button:
        :param state: Button state
        """

        if button == GbButtonId.EMU_QUIT:
            self._eventHandler.registerEvent(GbEventId.QUIT)
        elif button == GbButtonId.EMU_DEBUG and state == GbButtonState.PRESSED:
            self._eventHandler.registerEvent(GbEventId.DEBUG_TOGGLE)
        elif button == GbButtonId.EMU_SPEED:
            self._eventHandler.registerEvent(GbEventId.SPEED_CHANGED)
        elif button == GbButtonId.EMU_SAVE and state == GbButtonState.PRESSED:
            self._eventHandler.registerEvent(GbEventId.STATE_IO,
                    '{}.state'.format(self._mb.cartridge.filename), 'save')
        elif button == GbButtonId.EMU_LOAD and state == GbButtonState.PRESSED:
            self._eventHandler.registerEvent(GbEventId.STATE_IO,
                    '{}.state'.format(self._mb.cartridge.filename), 'load')
