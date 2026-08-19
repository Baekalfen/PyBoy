#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperPokemonGen1.cartridge_title": False,
    "GameWrapperPokemonGen1.post_tick": False,
}

import numpy as np

import pyboy
from pyboy.utils import bcd_to_dec, dec_to_bcd

from .base_plugin import PyBoyGameWrapper
from .game_wrapper_pokemon_gen1_constants import (
    BAG_ITEM_CAPACITY,
    BAG_ITEM_COUNT_ADDRESS,
    BAG_ITEMS_ADDRESS,
    BADGES,
    EVENT_FLAGS,
    EVENT_FLAGS_ADDRESS,
    MAPS,
    POKEMON_MOVES,
    POKEMON_SPECIES,
    POKEMON_SPECIES_NAMES,
    POKEMON_TEXT_DECODING,
    POKEMON_TEXT_ENCODING,
    TRAINER_CLASSES,
    TRAINER_CLASS_NAMES,
    TRAINER_SET_COUNTS,
    PARTY_COUNT_ADDRESS,
    PARTY_SPECIES_ADDRESS,
    PARTY_MONS_ADDRESS,
    PARTY_MON_SIZE,
    PARTY_LENGTH,
    PARTY_SPECIES_SENTINEL,
    NAME_LENGTH,
    TEXT_TERMINATOR,
    PLAYER_NAME_ADDRESS,
    PARTY_MON_OT_ADDRESS,
    PARTY_MON_NICKNAME_ADDRESS,
    DESTINATION_WARP_ID_ADDRESS,
    STATUS_FLAGS3_ADDRESS,
    WARP_DESTINATION_MAP_ADDRESS,
    BIT_WARP_FROM_CURRENT_SCRIPT,
    CURRENT_OPPONENT_ADDRESS,
    BATTLE_TYPE_ADDRESS,
    TRAINER_NUMBER_ADDRESS,
    CURRENT_ENEMY_LEVEL_ADDRESS,
    OPPONENT_ID_OFFSET,
    OBTAINED_BADGES_ADDRESS,
    ITEMS,
    ITEM_QUANTITY_MAX,
    MAX_MONEY,
    PLAYER_MONEY_ADDRESS,
    TRAINER_CLASS_COUNT,
)

logger = pyboy.logging.get_logger(__name__)


class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue, and provides basic access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.

    Example:
    ```python
    >>> pyboy = PyBoy(pokemon_blue_rom)
    >>> pyboy.game_wrapper.start_game()
    >>> pyboy.game_wrapper.add_pokemon("PIKACHU", level=5)
    >>> pyboy.game_wrapper.start_wild_battle("RATTATA", level=3)
    ```
    """

    cartridge_title = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, game_area_section=(0, 0, 20, 18), game_area_follow_scxy=True, **kwargs)
        self.sprite_offset = 0

    def _skip_dialogue(self, verbose):
        while self.pyboy.tilemap_window[18, 16] != 238:  # The text dialog 'arrow'
            self.pyboy.tick(10, verbose, False)

        self.pyboy.button("a")
        self.pyboy.tick(60, verbose, False)

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This navigates through the intro and menu to start the game
        at the first playable state.

        The title-screen state is saved, and using `reset_game`, you can get back to this point instantly.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.start_game()
        ```
        """
        verbose = False

        self.pyboy.tick(120, verbose, False)

        for _ in range(8000):
            if self.pyboy.tilemap_window[2, 2] == 141:  # New game
                break
            if self.pyboy.tilemap_window[2, 2] == 130:  # Continue
                raise Exception("Continue game")
            self.pyboy.button("start")
            self.pyboy.tick(10, verbose, False)
        else:
            raise Exception("Didn't find menu")

        self.pyboy.button("start")
        self.pyboy.tick(100, verbose, False)  # Transition to oak talking

        for _ in range(15):
            self._skip_dialogue(verbose)

        if self.pyboy.tilemap_window[2, 4] != 129:  # "B" in Blue
            raise Exception("Not name screen?")

        # Select "BLUE" name
        self.pyboy.button("down")
        self.pyboy.tick(10, verbose, False)
        self.pyboy.button("a")
        self.pyboy.tick(10, verbose, False)

        for _ in range(6):
            self._skip_dialogue(verbose)

        if self.pyboy.tilemap_window[2, 4] != 145:  # "R" in Red
            raise Exception("Not name screen?")

        # Select "RED" name
        self.pyboy.button("down")
        self.pyboy.tick(10, verbose, False)
        self.pyboy.button("a")
        self.pyboy.tick(10, verbose, False)

        for _ in range(8):
            self._skip_dialogue(verbose)

        # Shrinking transition to Mom's house
        self.pyboy.tick(240, verbose, False)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def _read_u16(self, address):
        return (self.pyboy.memory[address] << 8) | self.pyboy.memory[address + 1]

    def _write_u16(self, address, value):
        self.pyboy.memory[address] = (value >> 8) & 0xFF
        self.pyboy.memory[address + 1] = value & 0xFF

    def _decode_text(self, encoded, skip_invalid=False):
        decoded = []
        for value in encoded:
            if value == TEXT_TERMINATOR:
                break
            elif value in POKEMON_TEXT_DECODING:
                decoded.append(POKEMON_TEXT_DECODING[value])
            elif not skip_invalid:
                raise ValueError(f"Unknown pokered text character: {value:#x}")
        return "".join(decoded)

    def _encode_text(self, text, terminate=False):
        if isinstance(text, str):
            encoded = []
            tokens = sorted(POKEMON_TEXT_ENCODING, key=len, reverse=True)
            offset = 0
            while offset < len(text):
                for token in tokens:
                    if text.startswith(token, offset):
                        if token == "@":
                            raise ValueError("Text cannot contain the terminator")
                        encoded.append(POKEMON_TEXT_ENCODING[token])
                        offset += len(token)
                        break
                else:
                    raise ValueError(f"Unsupported pokered text character: {text[offset]!r}")
        else:
            encoded = list(text)
            if any(not 0 <= value <= 0xFF or value == TEXT_TERMINATOR for value in encoded):
                raise ValueError("Text bytes must be valid pokered text characters")
        return encoded + ([TEXT_TERMINATOR] if terminate else [])

    def _read_name(self, address):
        name = []
        for offset in range(NAME_LENGTH - 1):
            value = self.pyboy.memory[address + offset]
            if value == TEXT_TERMINATOR:
                break
            name.append(value)
        return tuple(name)

    def _write_name(self, address, name):
        if isinstance(name, str):
            encoded = self._encode_text(name.upper())
        else:
            encoded = list(name)
        if len(encoded) > NAME_LENGTH:
            raise ValueError(f"Names must contain at most {NAME_LENGTH - 1} characters")
        encoded.extend([TEXT_TERMINATOR] * (NAME_LENGTH - len(encoded)))
        for offset, value in enumerate(encoded):
            self.pyboy.memory[address + offset] = value

    def _read_party_mon(self, index):
        address = PARTY_MONS_ADDRESS + index * PARTY_MON_SIZE
        return {
            "species": self.pyboy.memory[address],
            "ot_name": self._read_name(PARTY_MON_OT_ADDRESS + index * NAME_LENGTH),
            "nickname": self._read_name(PARTY_MON_NICKNAME_ADDRESS + index * NAME_LENGTH),
            "hp": self._read_u16(address + 1),
            "level": self.pyboy.memory[address + 0x21],
            "status": self.pyboy.memory[address + 4],
            "type1": self.pyboy.memory[address + 5],
            "type2": self.pyboy.memory[address + 6],
            "catch_rate": self.pyboy.memory[address + 7],
            "moves": tuple(self.pyboy.memory[address + 8 + i] for i in range(4)),
            "ot_id": self._read_u16(address + 12),
            "exp": (
                self.pyboy.memory[address + 14] << 16
                | self.pyboy.memory[address + 15] << 8
                | self.pyboy.memory[address + 16]
            ),
            "hp_exp": self._read_u16(address + 17),
            "attack_exp": self._read_u16(address + 19),
            "defense_exp": self._read_u16(address + 21),
            "speed_exp": self._read_u16(address + 23),
            "special_exp": self._read_u16(address + 25),
            "dvs": self._read_u16(address + 27),
            "pp": tuple(self.pyboy.memory[address + 29 + i] for i in range(4)),
            "max_hp": self._read_u16(address + 0x22),
            "attack": self._read_u16(address + 0x24),
            "defense": self._read_u16(address + 0x26),
            "speed": self._read_u16(address + 0x28),
            "special": self._read_u16(address + 0x2A),
        }

    def _write_party_mon(self, index, pokemon):
        address = PARTY_MONS_ADDRESS + index * PARTY_MON_SIZE
        moves = tuple(pokemon.get("moves", (0x21, 0, 0, 0)))
        default_pp = tuple(35 if move else 0 for move in moves)
        pp = tuple(pokemon.get("pp", default_pp))
        if len(moves) != 4 or len(pp) != 4:
            raise ValueError("moves and pp must contain exactly four values")

        level = pokemon["level"]
        self.pyboy.memory[address] = pokemon["species"]
        self._write_u16(address + 1, pokemon["hp"])
        self.pyboy.memory[address + 3] = level
        self.pyboy.memory[address + 4] = pokemon.get("status", 0)
        self.pyboy.memory[address + 5] = pokemon.get("type1", 0)
        self.pyboy.memory[address + 6] = pokemon.get("type2", 0)
        self.pyboy.memory[address + 7] = pokemon.get("catch_rate", 45)
        for i, move in enumerate(moves):
            self.pyboy.memory[address + 8 + i] = move
        self._write_u16(address + 12, pokemon.get("ot_id", 0))
        exp = pokemon.get("exp", level**3)
        self.pyboy.memory[address + 14] = (exp >> 16) & 0xFF
        self.pyboy.memory[address + 15] = (exp >> 8) & 0xFF
        self.pyboy.memory[address + 16] = exp & 0xFF
        for offset, key in (
            (17, "hp_exp"),
            (19, "attack_exp"),
            (21, "defense_exp"),
            (23, "speed_exp"),
            (25, "special_exp"),
        ):
            self._write_u16(address + offset, pokemon.get(key, 0))
        self._write_u16(address + 27, pokemon.get("dvs", 0xFFFF))
        for i, move_pp in enumerate(pp):
            self.pyboy.memory[address + 29 + i] = move_pp
        self.pyboy.memory[address + 0x21] = level
        for offset, key in ((0x22, "max_hp"), (0x24, "attack"), (0x26, "defense"), (0x28, "speed"), (0x2A, "special")):
            self._write_u16(address + offset, pokemon[key])
        self._write_name(
            PARTY_MON_OT_ADDRESS + index * NAME_LENGTH,
            pokemon.get("ot_name", self._read_name(PLAYER_NAME_ADDRESS)),
        )
        self._write_name(
            PARTY_MON_NICKNAME_ADDRESS + index * NAME_LENGTH,
            pokemon.get("nickname", POKEMON_SPECIES_NAMES.get(pokemon["species"], "MON")),
        )

    @property
    def party(self):
        """Return the current party as a list of dictionaries."""

        count = self.pyboy.memory[PARTY_COUNT_ADDRESS]
        if count > PARTY_LENGTH:
            raise ValueError(f"Invalid party count: {count}")
        return [self._read_party_mon(index) for index in range(count)]

    @party.setter
    def party(self, party):
        self.set_party(party)

    def set_party(self, party):
        """
        Replace the party with up to six complete Gen I party records.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> from pyboy.plugins.game_wrapper_pokemon_gen1_constants import POKEMON_SPECIES
        >>> pyboy.game_wrapper.set_party([
        ...     {"species": POKEMON_SPECIES["PIDGEY"], "level": 5, "hp": 20, "max_hp": 20, "attack": 10, "defense": 10, "speed": 10, "special": 10},
        ...     {"species": POKEMON_SPECIES["MEWTWO"], "level": 5, "hp": 20, "max_hp": 20, "attack": 10, "defense": 10, "speed": 10, "special": 10},
        ... ])
        ```
        """

        party = list(party)
        if len(party) > PARTY_LENGTH:
            raise ValueError("A Pokemon party can contain at most six Pokemon")
        for pokemon in party:
            species = pokemon["species"]
            level = pokemon["level"]
            if not 1 <= species <= 0xBE:
                raise ValueError(f"Invalid Pokemon species ID: {species:#x}")
            if not 1 <= level <= 100:
                raise ValueError(f"Invalid Pokemon level: {level}")

        self.pyboy.memory[PARTY_COUNT_ADDRESS] = len(party)
        for index in range(PARTY_LENGTH + 1):
            self.pyboy.memory[PARTY_SPECIES_ADDRESS + index] = (
                party[index]["species"] if index < len(party) else PARTY_SPECIES_SENTINEL
            )
        for index, pokemon in enumerate(party):
            self._write_party_mon(index, pokemon)

        for index in range(len(party), PARTY_LENGTH):
            address = PARTY_MONS_ADDRESS + index * PARTY_MON_SIZE
            for offset in range(PARTY_MON_SIZE):
                self.pyboy.memory[address + offset] = 0
            self._write_name(PARTY_MON_OT_ADDRESS + index * NAME_LENGTH, ())
            self._write_name(PARTY_MON_NICKNAME_ADDRESS + index * NAME_LENGTH, ())

    def add_pokemon(self, species, level=2, moves=None, **kwargs):
        """
        Add a battle-ready Pokemon using a species ID from pokered's constants.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.add_pokemon("PIKACHU", level=5)
        >>> pyboy.game_wrapper.party[0]["species"]
        84
        ```
        """

        if len(self.party) == PARTY_LENGTH:
            raise ValueError("The party is full")
        if isinstance(species, str):
            species = POKEMON_SPECIES[species.upper()]
        moves = tuple(POKEMON_MOVES[move.upper()] if isinstance(move, str) else move for move in (moves or ()))
        if len(moves) > 4:
            raise ValueError("moves must contain at most four move IDs")
        moves += (0,) * (4 - len(moves))
        default_pp = tuple(35 if move else 0 for move in moves)
        max_hp = kwargs.pop("max_hp", level * 2 + 10)
        stats = {
            "attack": level + 5,
            "defense": level + 5,
            "speed": level + 5,
            "special": level + 5,
        }
        stats.update(kwargs.pop("stats", {}))
        pokemon = {
            "species": species,
            "level": level,
            "hp": kwargs.pop("hp", max_hp),
            "max_hp": max_hp,
            "moves": moves,
            "pp": kwargs.pop("pp", default_pp),
            **stats,
            **kwargs,
        }
        self.set_party(self.party + [pokemon])

    def remove_pokemon(self, index):
        """
        Remove a Pokemon from the party by its zero-based index.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.add_pokemon("PIKACHU", level=5)
        >>> pyboy.game_wrapper.remove_pokemon(0)
        ```
        """

        party = self.party
        if not 0 <= index < len(party):
            raise IndexError(f"Invalid party index: {index} of {len(party)-1}")
        del party[index]
        self.set_party(party)

    @property
    def money(self):
        """Return the player's money, from 0 through 999999."""

        value = int.from_bytes(self.pyboy.memory[PLAYER_MONEY_ADDRESS : PLAYER_MONEY_ADDRESS + 3], "big")
        return bcd_to_dec(value, byte_width=3, byteorder="big")

    def set_money(self, amount):
        """
        Set the player's money.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.set_money(999999)
        ```
        """

        if not isinstance(amount, int) or not 0 <= amount <= MAX_MONEY:
            raise ValueError(f"Money must be an integer from 0 to {MAX_MONEY}")
        value = dec_to_bcd(amount, byte_width=3, byteorder="big")
        self.pyboy.memory[PLAYER_MONEY_ADDRESS : PLAYER_MONEY_ADDRESS + 3] = value.to_bytes(3, "big")

    def _item_id(self, item):
        if isinstance(item, str):
            try:
                item = ITEMS[item.upper()]
            except KeyError as error:
                raise ValueError(f"Unknown item: {item}") from error
        if not isinstance(item, int) or not 1 <= item <= 0xFE:
            raise ValueError(f"Invalid item ID: {item}")
        return item

    @property
    def inventory(self):
        """Return the bag contents as a list of item and quantity dictionaries."""

        count = self.pyboy.memory[BAG_ITEM_COUNT_ADDRESS]
        if count > BAG_ITEM_CAPACITY:
            raise ValueError(f"Invalid bag item count: {count}")
        return [
            {
                "item": self.pyboy.memory[BAG_ITEMS_ADDRESS + 2 * index],
                "quantity": self.pyboy.memory[BAG_ITEMS_ADDRESS + 2 * index + 1],
            }
            for index in range(count)
        ]

    def set_inventory(self, inventory, force=False):
        """
        Replace the bag contents with item and quantity pairs.

        Items may be pokered IDs or names from ``ITEMS``. Quantities range
        from 1 to 99.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.set_inventory({"POTION": 20, "MASTER_BALL": 1})
        ```
        """

        if isinstance(inventory, dict):
            inventory = inventory.items()
        entries = []
        seen = set()
        for item, quantity in inventory:
            item = self._item_id(item)
            if item in seen:
                raise ValueError(f"Duplicate item: {item:#x}")
            if not isinstance(quantity, int) or (not force and (not 0 <= quantity <= ITEM_QUANTITY_MAX)):
                raise ValueError(f"Item quantity must be an integer from 1 to {ITEM_QUANTITY_MAX}")
            seen.add(item)
            entries.append((item, quantity))
        if len(entries) > BAG_ITEM_CAPACITY:
            raise ValueError(f"The bag can contain at most {BAG_ITEM_CAPACITY} item types")

        self.pyboy.memory[BAG_ITEM_COUNT_ADDRESS] = len(entries)
        for index in range(BAG_ITEM_CAPACITY):
            address = BAG_ITEMS_ADDRESS + 2 * index
            if index < len(entries):
                self.pyboy.memory[address] = entries[index][0]
                self.pyboy.memory[address + 1] = entries[index][1]
            else:
                self.pyboy.memory[address] = 0xFF
                self.pyboy.memory[address + 1] = 0

    def set_item(self, item, quantity, force=False):
        """Set one bag item's quantity, removing it when ``quantity`` is zero."""

        item = self._item_id(item)
        if not isinstance(quantity, int) or (not force and (not 0 <= quantity <= ITEM_QUANTITY_MAX)):
            raise ValueError(f"Item quantity must be an integer from 0 to {ITEM_QUANTITY_MAX}")
        inventory = {entry["item"]: entry["quantity"] for entry in self.inventory}
        if quantity:
            inventory[item] = quantity
        else:
            inventory.pop(item, None)
        preserve_forced_quantities = any(
            item_quantity == 0 or item_quantity > ITEM_QUANTITY_MAX for item_quantity in inventory.values()
        )
        self.set_inventory(inventory, force=force or preserve_forced_quantities)

    def remove_item(self, item, quantity=1):
        """Remove a quantity of an item from the bag."""

        item = self._item_id(item)
        inventory = {entry["item"]: entry["quantity"] for entry in self.inventory}
        if item not in inventory or not isinstance(quantity, int) or not 1 <= quantity <= inventory[item]:
            raise ValueError(f"Cannot remove quantity {quantity} of item {item:#x}")
        self.set_item(item, inventory[item] - quantity, force=inventory[item] > ITEM_QUANTITY_MAX)

    def start_wild_battle(self, species, level, force=False):
        """
        Schedule a wild battle against a species at the given level.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.add_pokemon("PIKACHU", level=5)
        >>> pyboy.game_wrapper.start_wild_battle("PIKACHU", level=5)
        >>> pyboy.tick(1)
        True
        ```
        """

        if isinstance(species, str):
            try:
                species = POKEMON_SPECIES[species.upper()]
            except KeyError as error:
                raise ValueError(f"Unknown Pokemon species: {species}") from error
        if not force:
            if not isinstance(species, int) or not 1 <= species <= 0xBE:
                raise ValueError(f"Invalid Pokemon species ID: {species}")
            if not isinstance(level, int) or not 1 <= level <= 100:
                raise ValueError(f"Invalid Pokemon level: {level}")

        self.pyboy.memory[CURRENT_OPPONENT_ADDRESS] = species
        self.pyboy.memory[CURRENT_ENEMY_LEVEL_ADDRESS] = level
        self.pyboy.memory[BATTLE_TYPE_ADDRESS] = 0

    def start_trainer_battle(self, trainer_class, trainer_set=1, force=False):
        """
        Schedule a trainer battle by class and party-set IDs.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.add_pokemon("PIKACHU", level=5)
        >>> pyboy.game_wrapper.start_trainer_battle("PROF_OAK", trainer_set=1)
        >>> pyboy.tick(1)
        True
        ```
        """

        if isinstance(trainer_class, str):
            try:
                trainer_class = TRAINER_CLASSES[trainer_class.upper()]
            except KeyError as error:
                raise ValueError(f"Unknown trainer class: {trainer_class}") from error
        if not force:
            if not isinstance(trainer_class, int) or not 1 <= trainer_class <= TRAINER_CLASS_COUNT:
                raise ValueError(f"Invalid trainer class ID: {trainer_class}")
            trainer_class_name = TRAINER_CLASS_NAMES[trainer_class]
            trainer_set_count = TRAINER_SET_COUNTS[trainer_class_name]
            if not isinstance(trainer_set, int) or not 1 <= trainer_set <= trainer_set_count:
                raise ValueError(f"Invalid trainer set ID: {trainer_set}")

        opponent = OPPONENT_ID_OFFSET + trainer_class
        self.pyboy.memory[CURRENT_OPPONENT_ADDRESS] = opponent
        self.pyboy.memory[TRAINER_NUMBER_ADDRESS] = trainer_set
        self.pyboy.memory[BATTLE_TYPE_ADDRESS] = 0

    def warp(self, destination):
        """
        Schedule a script warp to a map identified by name or ID.

        The map transition is performed by pokered on the next emulator tick.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.warp("viridian_pokecenter")
        >>> pyboy.tick(1)
        True
        ```
        """

        if isinstance(destination, str):
            try:
                map_id = MAPS[destination]
            except KeyError as error:
                raise ValueError(f"Unknown map name: {destination}") from error
        else:
            map_id = destination
        if not 0 <= map_id <= 0xFF:
            raise ValueError(f"Invalid map ID: {map_id:#x}")
        self.pyboy.memory[WARP_DESTINATION_MAP_ADDRESS] = map_id
        self.pyboy.memory[DESTINATION_WARP_ID_ADDRESS] = 0
        self.pyboy.memory[STATUS_FLAGS3_ADDRESS] |= 1 << BIT_WARP_FROM_CURRENT_SCRIPT

    def set_event_flag(self, event):
        """
        Set a story event flag by name or numeric pokered event ID.

        Gym victory event flags are separate from the badges owned by the
        player. Use :meth:`set_badge` to grant a badge.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.set_event_flag("got_pokedex")
        ```
        """
        event = EVENT_FLAGS.get(event, event)  # Try lookup or default to the original value
        if not isinstance(event, int):
            raise ValueError(f"Invalid event flag: {event}")
        address = EVENT_FLAGS_ADDRESS + event // 8
        self.pyboy.memory[address] |= 1 << (event % 8)

    def reset_event_flag(self, event):
        """
        Reset a story event flag by name or numeric pokered event ID.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.reset_event_flag("got_pokedex")
        ```
        """
        event = EVENT_FLAGS.get(event, event)  # Try lookup or default to the original value
        if not isinstance(event, int):
            raise ValueError(f"Invalid event flag: {event}")
        address = EVENT_FLAGS_ADDRESS + event // 8
        self.pyboy.memory[address] &= ~(1 << (event % 8))

    def set_badge(self, badge):
        """
        Grant a badge by name or numeric bit position.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.set_badge("boulder")
        ```
        """
        badge = BADGES.get(badge, badge)
        if not isinstance(badge, int) or not 0 <= badge < len(BADGES):
            raise ValueError(f"Invalid badge: {badge}")
        self.pyboy.memory[OBTAINED_BADGES_ADDRESS] |= 1 << badge

    def reset_badge(self, badge):
        """
        Remove a badge by name or numeric bit position.

        Example:
        ```python
        >>> pyboy = PyBoy(pokemon_blue_rom)
        >>> pyboy.game_wrapper.reset_badge("boulder")
        ```
        """
        badge = BADGES.get(badge, badge)
        if not isinstance(badge, int) or not 0 <= badge < len(BADGES):
            raise ValueError(f"Invalid badge: {badge}")
        self.pyboy.memory[OBTAINED_BADGES_ADDRESS] &= ~(1 << badge)

    def enabled(self):
        return (self.pyboy.cartridge_title == "POKEMON RED") or (self.pyboy.cartridge_title == "POKEMON BLUE")

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        scanline_parameters = self.pyboy.screen.tilemap_position_list
        # WX = scanline_parameters[0][2]
        WY = scanline_parameters[0][3]
        self.use_background(WY != 0)

    def _get_screen_background_tilemap(self):
        ### SIMILAR TO CURRENT pyboy.game_wrapper.game_area(), BUT ONLY FOR BACKGROUND TILEMAP, SO NPC ARE SKIPPED
        ((scx, scy), (wx, wy)) = self.pyboy.screen.get_tilemap_position()
        tilemap = np.array(self.pyboy.tilemap_background[:, :])
        return np.roll(np.roll(tilemap, -scy // 8, axis=0), -scx // 8, axis=1)[:18, :20]

    def _get_screen_walkable_matrix(self):
        walkable_tiles_indexes = []
        collision_ptr = self.pyboy.memory[0xD530] + (self.pyboy.memory[0xD531] << 8)
        tileset_type = self.pyboy.memory[0xFFD7]
        if tileset_type > 0:
            grass_tile_index = self.pyboy.memory[0xD535]
            if grass_tile_index != 0xFF:
                walkable_tiles_indexes.append(grass_tile_index + 0x100)
        for i in range(0x180):
            tile_index = self.pyboy.memory[collision_ptr + i]
            if tile_index == 0xFF:
                break
            else:
                walkable_tiles_indexes.append(tile_index + 0x100)
        screen_tiles = self._get_screen_background_tilemap()
        bottom_left_screen_tiles = screen_tiles[1 : 1 + screen_tiles.shape[0] : 2, ::2]
        walkable_matrix = np.isin(bottom_left_screen_tiles, walkable_tiles_indexes).astype(np.uint8)
        return walkable_matrix

    def game_area_collision(self):
        width = self.game_area_section[2]
        height = self.game_area_section[3]
        game_area = np.ndarray(shape=(height, width), dtype=np.uint32)
        _collision = self._get_screen_walkable_matrix()
        for i in range(height // 2):
            for j in range(width // 2):
                game_area[i * 2][j * 2 : j * 2 + 2] = _collision[i][j]
                game_area[i * 2 + 1][j * 2 : j * 2 + 2] = _collision[i][j]
        return game_area

    def __repr__(self):
        return "Pokemon Gen 1:\n" + super().__repr__()
