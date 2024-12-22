#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging import get_logger
from pyboy.utils import PyBoyInvalidInputException

logger = get_logger(__name__)

__pdoc__ = {
    "GameShark.tick": False,
}


class GameShark:
    def __init__(self, memory):
        self.memory = memory
        self.cheats = {}
        self.enabled = False

    def _convert_cheat(self, gameshark_code):
        """
        A GameShark code for these consoles is written in the format ttvvaaaa. tt specifies the type, which is usually 01.
        vv specifies the hexadecimal value the code will write into the game's memory. aaaa specifies the memory address
        that will be modified, with the low byte first (e.g. address C056 is written as 56C0).
        Example 011556C0 would output:
        type = 01
        value = 0x15
        address = 0x56C0

        For more details:
        https://doc.kodewerx.org/hacking_gb.html

        There seems to be conflicting information about the presence of other types than 01.
        """
        # Check if the input cheat code has the correct length (8 characters)
        if len(gameshark_code) != 8:
            raise ValueError("Invalid cheat code length. Cheat code must be 8 characters long.")

        # Extract components from the cheat code
        _type = int(gameshark_code[:2], 16)
        value = int(gameshark_code[2:4], 16)  # Convert hexadecimal value to an integer
        unconverted_address = gameshark_code[4:]  # Ex:   1ED1
        lower = unconverted_address[:2]  # Ex:  1E
        upper = unconverted_address[2:]  # Ex:  D1
        address_converted = upper + lower  # Ex: 0xD11E   # Converting to Ram Readable address
        address = int(address_converted, 16)

        if not 0x8000 <= address:
            raise ValueError("Invalid GameShark code provided. Address not in the RAM range")

        return (_type, value, address)

    def _get_value(self, _type, address):
        if _type == 0x01:
            # 8-bit RAM write
            # Writes the byte xx to the address zzyy.
            return self.memory[address]
        # elif (_type & 0xF0) == 0x80:
        #     # 8-bit RAM write (with bank change)
        #     # Changes the RAM bank to b, then writes the byte xx to the address zzyy.
        #     bank = _type & 0xF
        #     pass
        # elif (_type & 0xF0) == 0x90:
        #     # 8-bit RAM write (with WRAM bank change)
        #     # Changes the WRAM bank to b and then writes the byte xx to the address zzyy. GBC only.
        #     bank = _type & 0xF
        #     pass
        else:
            raise ValueError("Invalid GameShark type", _type)

    def _set_value(self, _type, value, address):
        if _type == 0x01:
            # 8-bit RAM write
            # Writes the byte xx to the address zzyy.
            self.memory[address] = value
        # elif (_type & 0xF0) == 0x80:
        #     # 8-bit RAM write (with bank change)
        #     # Changes the RAM bank to b, then writes the byte xx to the address zzyy.
        #     bank = _type & 0xF
        #     pass
        # elif (_type & 0xF0) == 0x90:
        #     # 8-bit RAM write (with WRAM bank change)
        #     # Changes the WRAM bank to b and then writes the byte xx to the address zzyy. GBC only.
        #     bank = _type & 0xF
        #     pass
        else:
            raise ValueError("Invalid GameShark type", _type)

    def add(self, code):
        """
        Add a GameShark cheat to the emulator.

        Example:
        ```python
        >>> pyboy.gameshark.add("01FF16D0")
        ```

        Args:
            code (str): GameShark code to add
        """
        self.enabled = True
        _type, value, address = self._convert_cheat(code)
        if code not in self.cheats:
            self.cheats[code] = (self._get_value(_type, address), (_type, value, address))
        else:
            raise PyBoyInvalidInputException("GameShark code already applied!")

    def remove(self, code, restore_value=True):
        """
        Remove a GameShark cheat from the emulator.

        Example:
        ```python
        >>> pyboy.gameshark.add("01FF16D0")
        >>> pyboy.gameshark.remove("01FF16D0")
        ```

        Args:
            code (str): GameShark code to remove
            restore_value (bool): True to restore original value at address, otherwise don't restore
        """

        if code not in self.cheats:
            raise ValueError("GameShark code cannot be removed. Hasn't been applied.")

        original_value, (_type, _, address) = self.cheats.pop(code)
        if restore_value:
            self._set_value(_type, original_value, address)

        if len(self.cheats) == 0:
            self.enabled = False

    def clear_all(self, restore_value=True):
        """
        Remove all GameShark cheats from the emulator.

        Example:
        ```python
        >>> pyboy.gameshark.clear_all()
        ```

        Args:
            restore_value (bool): Restore the original values of the memory addresses that were modified by the cheats.
        """
        # NOTE: Create a list so we don't remove from the iterator we are going through
        for code in list(self.cheats.keys()):
            self.remove(code, restore_value)

    def tick(self):
        if not self.enabled:
            return 0
        # https://gbdev.io/pandocs/Shark_Cheats.html
        # "As far as it is understood, patching is implemented by hooking the original VBlank interrupt handler, and
        # re-writing RAM values each frame."
        for _, (_, (_type, value, address)) in self.cheats.items():
            self._set_value(_type, value, address)
