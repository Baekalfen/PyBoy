#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from . import windowevent


P10, P11, P12, P13 = range(4)


def reset_bit(x, bit):
    return x & ~(1 << bit)


def set_bit(x, bit):
    return x | (1 << bit)


class Interaction:
    def __init__(self):
        self.directional = 0xF
        self.standard = 0xF

    def key_event(self, key):
        if key == windowevent.PRESS_ARROW_RIGHT:
            self.directional = reset_bit(self.directional, P10)
        elif key == windowevent.PRESS_ARROW_LEFT:
            self.directional = reset_bit(self.directional, P11)
        elif key == windowevent.PRESS_ARROW_UP:
            self.directional = reset_bit(self.directional, P12)
        elif key == windowevent.PRESS_ARROW_DOWN:
            self.directional = reset_bit(self.directional, P13)

        elif key == windowevent.PRESS_BUTTON_A:
            self.standard = reset_bit(self.standard, P10)
        elif key == windowevent.PRESS_BUTTON_B:
            self.standard = reset_bit(self.standard, P11)
        elif key == windowevent.PRESS_BUTTON_SELECT:
            self.standard = reset_bit(self.standard, P12)
        elif key == windowevent.PRESS_BUTTON_START:
            self.standard = reset_bit(self.standard, P13)

        elif key == windowevent.RELEASE_ARROW_RIGHT:
            self.directional = set_bit(self.directional, P10)
        elif key == windowevent.RELEASE_ARROW_LEFT:
            self.directional = set_bit(self.directional, P11)
        elif key == windowevent.RELEASE_ARROW_UP:
            self.directional = set_bit(self.directional, P12)
        elif key == windowevent.RELEASE_ARROW_DOWN:
            self.directional = set_bit(self.directional, P13)

        elif key == windowevent.RELEASE_BUTTON_A:
            self.standard = set_bit(self.standard, P10)
        elif key == windowevent.RELEASE_BUTTON_B:
            self.standard = set_bit(self.standard, P11)
        elif key == windowevent.RELEASE_BUTTON_SELECT:
            self.standard = set_bit(self.standard, P12)
        elif key == windowevent.RELEASE_BUTTON_START:
            self.standard = set_bit(self.standard, P13)

    def pull(self, joystickbyte):
        P14 = (joystickbyte >> 4) & 1
        P15 = (joystickbyte >> 5) & 1
        # Bit 7 - Not used (No$GMB)
        # Bit 6 - Not used (No$GMB)
        # Bit 5 - P15 out port
        # Bit 4 - P14 out port
        # Bit 3 - P13 in port
        # Bit 2 - P12 in port
        # Bit 1 - P11 in port
        # Bit 0 - P10 in port

        # Guess to make first 4 and last 2 bits true, while keeping selected bits
        joystickByte = 0xFF & (joystickbyte | 0b11001111)
        if P14 and P15:
            pass
        elif not P14 and not P15:
            pass
        elif not P14:
            joystickByte &= self.directional
        elif not P15:
            joystickByte &= self.standard

        return joystickByte
