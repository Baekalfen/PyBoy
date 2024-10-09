#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperPokemonRed.cartridge_title": False,
    "GameWrapperPokemonRed.post_tick": False,
}

from pyboy.utils import WindowEvent
from pyboy.logger import logger
from ..base_plugin import PyBoyGameWrapper
from . import constants
from .utils import get_character_index

PKMN_SIZE = 0x2C
BYTE_ORDER = 'big'


try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperPokemonRed(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red, and provides easy access to score and a "fitness" score for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = "POKEMON RED"

    def __init__(self, *args, **kwargs):
        # TODO: Determine proper size
        self.shape = (20, 16)
        """The shape of the game area"""
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        while self.get_player_name() != 'NINTEN': # Player is NINTEN on start screen
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

    def get_int_at_address(self, address, size=2):
        """Returns an integer from a given address of a specified size."""
        bytes = []
        for i in range(size):
            bytes.append(self.pyboy.get_memory_value(address + i))
        return int.from_bytes(bytes, byteorder=BYTE_ORDER)

    def set_int_at_address(self, address, value, size=2):
        """Sets an integer at a given address of a specified size."""
        bytes = value.to_bytes(2, byteorder=BYTE_ORDER)
        i = 0
        for byte in bytes:
            self.pyboy.set_memory_value(address + i, byte)
            i += 1

    def set_text(self, text, address):
        """Sets text at address.

        Will always add a string terminator (80) at the end.
        """
        i = 0
        for character in text:
            try:
                self.pyboy.set_memory_value(address + i, get_character_index(character))
                i += 1
            except:
                pass
        self.pyboy.set_memory_value(address + i, constants.STRING_TERMINATOR)

    def set_rom_text(self, text, bank, address):
        i = 0
        for character in text:
            try:
                self.pyboy.override_memory_value(bank, address + i, get_character_index(character))
                i += 1
            except:
                pass

    def set_player_name(self, name):
        """
        Sets the player name.

        Args:
            name (string): Name to be set (will be trimmed at 8 characters).
        """
        self.set_text(name[:8], 0xD158)

    def get_player_name(self):
        """
        Returns player name.
        """
        return self.get_text(0xD158)

    def set_rival_name(self, name):
        """
        Sets the rival name.

        Args:
            name (string): Name to be set (will be trimmed at 8 characters).
        """
        self.set_text(name[:8], 0xD34A)

    def get_rival_name(self):
        """
        Returns rival name.
        """
        return self.get_text(0xD34A)

    def get_text(self, address, cap = 16):
        """
        Retrieves a string from a given address.

        Args:
            address (int): Address from where to retrieve text from.
            cap (int): Maximum expected length of string (default: 16).
        """
        i = 0
        text = ''
        while i < cap:
            value = self.pyboy.get_memory_value(address + i)
            try:
                text += chr(value - constants.ASCII_DELTA)
            except:
                pass
            if value == constants.STRING_TERMINATOR:
                break
            i += 1
        return text

    def set_palette_to_darkness(self):
        self.pyboy.set_memory_value(0xD35D, 6)

    def set_player_monster(self, index, monster):
        """
        Sets player monster at a given index.

        Args:
            index (int): Which monster to change (0-5).
            monster (int): Which type of monster to set.
        """
        self.pyboy.set_memory_value(0xD16B + index, monster)
        self.pyboy.set_memory_value(0xD164 + (index * PKMN_SIZE), monster)

    def get_player_monster(self, index):
        """
        Returns player monster at a given index.

        Args:
            index (int): Which monster to change (0-5).
        """
        return self.pyboy.get_memory_value(0xD16B + index)

    def set_player_monster_nickname(self, index, text):
        """
        Sets player monster's nickname at a given index.

        Args:
            index (int): Which monster to change (0-5).
            text (string): Nickname to set (will be trimmed at 10 characters).
        """
        self.set_text(text[:10], 0xD2B5 + (index * PKMN_SIZE))

    def get_player_monster_nickname(self, index):
        """
        Returns player monster's nickname at a given index.

        Args:
            index (int): Which monster (0-5).
        """
        return self.get_text(0xD2B5 + (index * PKMN_SIZE))

    def set_player_monster_move(self, index, move_index, move):
        """
        Sets player monster's move at a given index.

        Args:
            index (int): Which monster to change (0-5).
            move_index (int): Which move to change (0-3).
            move (int): Which type of move to set.
        """
        self.pyboy.set_memory_value(0xD01C + (index * PKMN_SIZE) + move_index, move)

    def get_player_monster_move(self, index, move_index):
        """
        Returns player monster's move at a given index.

        Args:
            index (int): Which monster (0-5).
            move_index (int): Which move to change (0-3).
        """
        return self.pyboy.get_memory_value(0xD01C + (index * PKMN_SIZE) + move_index)

    def get_player_monster_current_hp(self, index):
        """
        Returns player monster's current HP at a given index.

        Args:
            index (int): Which monster (0-5).
        """
        return self.get_int_at_address(0xD16C + (index * PKMN_SIZE))

    def get_active_player_monster_current_hp(self):
        return self.get_int_at_address(0xD015)

    def set_player_monster_current_hp(self, index, hp):
        """
        Sets the current HP of a given player monster.

        Args:
            index (int): Which monster to change (0-5).
            hp (int): Health points.
        """
        self.set_int_at_address(0xD16C + (index * PKMN_SIZE), hp)

    def set_active_player_monster_current_hp(self, hp):
        self.set_int_at_address(0xD015, hp)

    def get_player_monster_max_hp(self, index):
        """
        Returns player monster's max HP at a given index.

        Args:
            index (int): Which monster (0-5).
        """
        return self.get_int_at_address(0xD18D + (index * PKMN_SIZE))

    def get_active_player_monster_max_hp(self):
        return self.get_int_at_address(0xD023)

    def set_player_monster_max_hp(self, index, hp):
        """
        Sets the max HP of a given player monster.

        Args:
            index (int): Which monster to change (0-5).
            hp (int): Health points.
        """
        self.set_int_at_address(0xD18D + (index * PKMN_SIZE), hp)

    def set_active_player_monster_max_hp(self, hp):
        return self.set_int_at_address(0xD023, hp)

    def set_player_monster_status(self, index, status):
        """
        Sets the ailment status of a given player monster.

        Args:
            index (int): Which monster to change (0-5).
            status (int): Status to be set.
        """
        assert status >= 0 and status < 0xFF
        assert index < 6
        self.pyboy.set_memory_value(0xD16F + (index * PKMN_SIZE), status)

    def set_player_monster_asleep(self, index):
        self.set_player_monster_status(index, constants.STATUS_ASLEEP)

    def set_player_monster_poisoned(self, index):
        self.set_player_monster_status(index, constants.STATUS_POISONED)

    def set_player_monster_burned(self, index):
        self.set_player_monster_status(index, constants.STATUS_BURNED)

    def set_player_monster_frozen(self, index):
        self.set_player_monster_status(index, constants.STATUS_FROZEN)

    def set_player_monster_paralyzed(self, index):
        self.set_player_monster_status(index, constants.STATUS_PARALYZED)

    def set_player_monster_no_ailment(self, index):
        self.set_player_monster_status(index, 0)

    def get_player_money(self):
        return self.get_int_at_address(0xD347, size=3)

    def set_active_player_monster_status(self, status):
        self.pyboy.set_memory_value(0xD018, status)

    def set_active_player_monster_asleep(self):
        self.set_active_player_monster_status(constants.STATUS_ASLEEP)

    def set_active_player_monster_poisoned(self):
        self.set_active_player_monster_status(constants.STATUS_POISONED)

    def set_active_player_monster_burned(self):
        self.set_active_player_monster_status(constants.STATUS_BURNED)

    def set_active_player_monster_frozen(self):
        self.set_active_player_monster_status(constants.STATUS_FROZEN)

    def set_active_player_monster_paralyzed(self):
        self.set_active_player_monster_status(constants.STATUS_PARALYZED)

    def set_active_player_monster_no_ailment(self):
        self.set_active_player_monster_status(0)

    def set_active_player_monster_move(self, index, move):
        self.pyboy.set_memory_value(0xD01C + index, move)

    def set_active_opponent_monster_move(self, index, move):
        self.pyboy.set_memory_value(0xCFED + index, move)

    def set_active_player_monster_nickname(self, nickname):
        self.set_text(nickname[:10], 0xD009)

    def set_active_opponent_monster_nickname(self, nickname):
        self.set_text(nickname[:10], 0xCFDA)

    def set_active_opponent_monster_status(self, status):
        self.pyboy.set_memory_value(0xCFE9, status)

    def set_active_opponent_monster_asleep(self):
        self.set_active_opponent_monster_status(constants.STATUS_ASLEEP)

    def set_active_opponent_monster_poisoned(self):
        self.set_active_opponent_monster_status(constants.STATUS_POISONED)

    def set_active_opponent_monster_burned(self):
        self.set_active_opponent_monster_status(constants.STATUS_BURNED)

    def set_active_opponent_monster_frozen(self):
        self.set_active_opponent_monster_status(constants.STATUS_FROZEN)

    def set_active_opponent_monster_paralyzed(self):
        self.set_active_opponent_monster_status(constants.STATUS_PARALYZED)

    def set_active_opponent_monster_no_ailment(self):
        self.set_active_opponent_monster_status(0)

    def heal_player_monster(self, index):
        """
        Fully heals a player monster.

        Args:
            index (int): Which monster to change (0-5).
        """
        self.set_player_monster_no_ailment(index)
        max_hp = self.get_player_monster_max_hp(index)
        self.set_player_monster_current_hp(index, max_hp)

    def heal_active_player_monster(self):
        self.set_active_player_monster_no_ailment()
        max_hp = self.get_active_player_monster_max_hp()
        self.set_active_player_monster_current_hp(max_hp)

    def is_battle_happening(self):
        return self.pyboy.get_memory_value(0xD057) != 0

    def get_current_map(self):
        return self.pyboy.get_memory_value(0xD35E)

    def get_current_map_name(self):
        return constants.MAP_NAMES[self.get_current_map()]

    def set_wild_encounter_rate(self, value):
        self.pyboy.set_memory_value(0xD887, value)

    # TODO: Add player position functions
