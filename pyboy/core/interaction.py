#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.utils import WindowEvent

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
        _directional = self.directional
        _standard = self.standard
        if key == WindowEvent.PRESS_ARROW_RIGHT:
            self.directional = reset_bit(self.directional, P10)
        elif key == WindowEvent.PRESS_ARROW_LEFT:
            self.directional = reset_bit(self.directional, P11)
        elif key == WindowEvent.PRESS_ARROW_UP:
            self.directional = reset_bit(self.directional, P12)
        elif key == WindowEvent.PRESS_ARROW_DOWN:
            self.directional = reset_bit(self.directional, P13)

        elif key == WindowEvent.PRESS_BUTTON_A:
            self.standard = reset_bit(self.standard, P10)
        elif key == WindowEvent.PRESS_BUTTON_B:
            self.standard = reset_bit(self.standard, P11)
        elif key == WindowEvent.PRESS_BUTTON_SELECT:
            self.standard = reset_bit(self.standard, P12)
        elif key == WindowEvent.PRESS_BUTTON_START:
            self.standard = reset_bit(self.standard, P13)

        elif key == WindowEvent.RELEASE_ARROW_RIGHT:
            self.directional = set_bit(self.directional, P10)
        elif key == WindowEvent.RELEASE_ARROW_LEFT:
            self.directional = set_bit(self.directional, P11)
        elif key == WindowEvent.RELEASE_ARROW_UP:
            self.directional = set_bit(self.directional, P12)
        elif key == WindowEvent.RELEASE_ARROW_DOWN:
            self.directional = set_bit(self.directional, P13)

        elif key == WindowEvent.RELEASE_BUTTON_A:
            self.standard = set_bit(self.standard, P10)
        elif key == WindowEvent.RELEASE_BUTTON_B:
            self.standard = set_bit(self.standard, P11)
        elif key == WindowEvent.RELEASE_BUTTON_SELECT:
            self.standard = set_bit(self.standard, P12)
        elif key == WindowEvent.RELEASE_BUTTON_START:
            self.standard = set_bit(self.standard, P13)

        # XOR to find the changed bits, AND it to see if it was high before.
        # Test for both directional and standard buttons.
        return ((_directional ^ self.directional) & _directional) or ((_standard ^ self.standard) & _standard)

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
            joystickByte = 0xF
        elif not P14 and not P15:
            pass  # FIXME: What happens when both are requested?
        elif not P14:
            joystickByte &= self.directional
        elif not P15:
            joystickByte &= self.standard

        return joystickByte | 0b11000000

    def save_state(self, f):
        f.write(self.directional)
        f.write(self.standard)

    def load_state(self, f, state_version):
        if state_version >= 7:
            self.directional = f.read()
            self.standard = f.read()
        else:
            self.directional = 0xF
            self.standard = 0xF
