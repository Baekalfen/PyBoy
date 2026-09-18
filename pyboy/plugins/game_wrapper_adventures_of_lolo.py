#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperAdventuresOfLolo.cartridge_title": False,
    "GameWrapperAdventuresOfLolo.post_tick": False,
}

import io

import numpy as np

import pyboy
from pyboy.api.constants import TILES
from pyboy.utils import PyBoyException, PyBoyInvalidInputException, PyBoyOutOfBoundsException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# Bank 13 holds the room table, flat and uncompressed: 0x4000 + N*64. 16 KiB over 64 bytes
# gives 256 slots, and only the first 163 are rooms.
ROOM_TABLE_BANK = 13
ROOM_TABLE_ADDR = 0x4000
ROOM_BYTES = 64
ROOM_COUNT = 163
ROOM_SIDE = 8

# How the rooms are grouped. The cartridge computes `floor = (room - 38) // 14` and
# `level = (room - 38) % 14`, which fixes where the tutorial ends and the graded rooms begin.
TUTORIAL_PAIRS = 19  # Each tutorial puzzle is stored twice: a demonstration, then a room
TUTORIAL_END = 2 * TUTORIAL_PAIRS  # 38
INTERMEDIATE_START, INTERMEDIATE_PER_FLOOR = 38, 14
ADVANCED_START, ADVANCED_PER_FLOOR = 108, 5
PRO_START = 158

ROOM_NUMBER_ADDR = 0xC3A6  # Index into the bank 13 room table
FLOOR_ADDR = 0xC3A4  # (room - 38) // 14
LEVEL_IN_FLOOR_ADDR = 0xC3A5  # (room - 38) % 14
HEARTS_LEFT_ADDR = 0xC3A9  # Heart framers still to collect: the status bar's number
MAGIC_SHOTS_ADDR = 0xC4AD  # +2 per magic heart framer, -1 per shot
SCENE_ADDR = 0xC3BE  # Which screen the game is running
BOARD_ADDR = 0xC3BF  # The room as loaded, 8 by 8, and never updated afterwards
OAM_BUFFER_ADDR = 0xC000  # OAM DMA source: 40 sprites of 4 bytes
OAM_BUFFER_BYTES = 160
LOLO_SPRITE_BYTES = 8  # Lolo is slots 0 and 1, the pair `settle` watches

# The scene while a graded room is being played. The tutorial's demonstration rooms run as
# 0x14 and play themselves, which is the one boot outcome that has to be rejected rather than
# merely waited out: a self-playing board answers every button with a move nobody asked for.
SCENE_PLAYING = 0x17
SCENE_TUTORIAL_DEMO = 0x14

# `LD A,($C3A6)` inside LoadRoom, three instructions past the bank switch. Hooking the entry
# point at 0x11E5 would be one instruction too early to matter and one bank switch too soon
# to be safe; hooking here puts the write between the caller's choice of room and the
# loader's read of it.
LOAD_ROOM_READ = 0x11EC
ROM_BANK = 0

# The cell codes. Most of the map is families of four consecutive codes, one per facing,
# which is why the table below is built rather than written out.
CODE_LOLO = 0x00  # Where Lolo starts
CODE_TREE = 0x80
CODE_ROCK = 0x81
CODE_RIVER_MIN, CODE_RIVER_MAX = 0x82, 0x87
CODE_FLOOR = 0x88
CODE_BRIDGE_MIN, CODE_BRIDGE_MAX = 0x89, 0x8A
CODE_ONE_WAY_MIN, CODE_ONE_WAY_MAX = 0x8B, 0x8E
CODE_FRAMER = 0x8F  # Emerald Framer: the block Lolo pushes
CODE_HEART = 0x90
CODE_MAGIC_HEART = 0x91
CODE_DESERT = 0x92
CODE_BREAK_TILE_MIN, CODE_BREAK_TILE_MAX = 0x93, 0x94
CODE_FLOWER_BED = 0x95
CODE_DOOR = 0x96
CODE_MARKER_MIN, CODE_MARKER_MAX = 0x97, 0x9C
CODE_BREAK_TILE = 0x9F
CODE_ENEMY_MIN, CODE_ENEMY_MAX = 0x04, 0x23  # Eight families of four facings

# Two codes the cartridge never writes. The board buffer is the room as it was *loaded* and
# is never touched again, so where an actor is now, and whether the door has opened, are read
# off the screen and written into the game area under codes of their own.
CODE_ENEMY = 0x01
CODE_DOOR_OPEN = 0x02

ENEMY_NAMES = ("LEEPER", "ROCKY", "ALMA", "GOL", "SKULL", "SNAKEY", "MEDUSA", "DON MEDUSA")

CELL_GLYPHS = {
    CODE_LOLO: "@",
    CODE_ENEMY: "e",
    CODE_DOOR_OPEN: "d",
    CODE_TREE: "T",
    CODE_ROCK: "#",
    CODE_FLOOR: ".",
    CODE_FRAMER: "O",
    CODE_HEART: "H",
    CODE_MAGIC_HEART: "h",
    CODE_DESERT: ",",
    CODE_FLOWER_BED: "*",
    CODE_DOOR: "D",
    CODE_BREAK_TILE: "x",
}
for _code in range(CODE_RIVER_MIN, CODE_RIVER_MAX + 1):
    CELL_GLYPHS[_code] = "~"
for _code in range(CODE_BRIDGE_MIN, CODE_BRIDGE_MAX + 1):
    CELL_GLYPHS[_code] = "="
for _code, _glyph in zip(range(CODE_ONE_WAY_MIN, CODE_ONE_WAY_MAX + 1), "v<^>"):
    CELL_GLYPHS[_code] = _glyph
for _code in range(CODE_BREAK_TILE_MIN, CODE_BREAK_TILE_MAX + 1):
    CELL_GLYPHS[_code] = "x"
for _code in range(CODE_MARKER_MIN, CODE_MARKER_MAX + 1):
    CELL_GLYPHS[_code] = "o"
for _family, _glyph in enumerate("LRAGKSMN"):
    for _facing in range(4):
        CELL_GLYPHS[CODE_ENEMY_MIN + 4 * _family + _facing] = _glyph

# Driving the cartridge. Lolo lives on a half-cell grid: a d-pad press held 1-14 frames moves
# him 8 pixels, half a cell, and 16-28 frames moves a whole one.
PRESS_TICKS = 20  # One whole cell
HALF_STEP_TICKS = 8  # ... and half of one
SHOOT_TICKS = 6  # The magic shot is an edge, not a hold
SETTLE_MAX_TICKS = 300
SETTLE_STABLE_TICKS = 8  # Frames Lolo's own sprite must hold still
SETTLE_MIN_TICKS = 18  # ... and the fewest frames any action runs, so a shot lands

BOOT_TITLE_TICKS = 400  # The title screen's own animation, before it takes input
BOOT_MENU_TICKS = 120
BOOT_STORY_TICKS = 40  # One line of the King's introduction
BOOT_ROOM_TICKS = 24
BOOT_MAX_ROOM_PRESSES = 500
# How many taps of A walk the King's introduction from the NEW GAME wheel to its last screen,
# the one offering "Push A: ENTRY / Push B: INTERMEDIATE". Being one screen out drops the boot
# into the tutorial, whose demonstration rooms play themselves, so the count is checked
# afterwards and the neighbours are tried when it lands somewhere else.
BOOT_STORY_ALTERNATIVES = (27, 28, 26, 29, 25)

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
mapping_compressed[CODE_FLOOR] = 1
mapping_compressed[CODE_ROCK] = 2
mapping_compressed[CODE_TREE] = 3
mapping_compressed[CODE_RIVER_MIN : CODE_RIVER_MAX + 1] = 4
mapping_compressed[CODE_BRIDGE_MIN : CODE_BRIDGE_MAX + 1] = 5
mapping_compressed[CODE_ONE_WAY_MIN : CODE_ONE_WAY_MAX + 1] = 6
mapping_compressed[CODE_FRAMER] = 7
mapping_compressed[CODE_HEART] = 8
mapping_compressed[CODE_MAGIC_HEART] = 9
mapping_compressed[CODE_DESERT] = 10
mapping_compressed[CODE_BREAK_TILE_MIN : CODE_BREAK_TILE_MAX + 1] = 11
mapping_compressed[CODE_BREAK_TILE] = 11
mapping_compressed[CODE_FLOWER_BED] = 12
mapping_compressed[CODE_MARKER_MIN : CODE_MARKER_MAX + 1] = 13
mapping_compressed[CODE_DOOR] = 14
mapping_compressed[CODE_DOOR_OPEN] = 15
mapping_compressed[CODE_LOLO] = 16
mapping_compressed[CODE_ENEMY] = 17
mapping_compressed[CODE_ENEMY_MIN : CODE_ENEMY_MAX + 1] = 17
"""
Compressed mapping for `pyboy.PyBoy.game_area_mapping`
"""

mapping_minimal = np.zeros(TILES, dtype=np.uint8)
mapping_minimal[CODE_ROCK] = 1
mapping_minimal[CODE_TREE] = 1
mapping_minimal[CODE_RIVER_MIN : CODE_RIVER_MAX + 1] = 1
mapping_minimal[CODE_FRAMER] = 2
mapping_minimal[CODE_HEART] = 3
mapping_minimal[CODE_MAGIC_HEART] = 3
mapping_minimal[CODE_DOOR] = 4
mapping_minimal[CODE_DOOR_OPEN] = 5
mapping_minimal[CODE_LOLO] = 6
mapping_minimal[CODE_ENEMY] = 7
mapping_minimal[CODE_ENEMY_MIN : CODE_ENEMY_MAX + 1] = 7
"""
Minimal mapping for `pyboy.PyBoy.game_area_mapping`
"""


def _cell_of(sprite_y, sprite_x):
    """An OAM entry's ``(y, x)`` as a cell, in halves.

    A sprite sits 16 pixels below and 8 to the right of where it draws, and the playfield's
    top-left cell starts at screen (8, 8). Returned as floats because Lolo genuinely stands on
    half-cells: (4.0, 3.5) is a real, reachable position, and rounding it away would make two
    different positions look like one.
    """
    return ((sprite_y - 24) / 16.0, (sprite_x - 16) / 16.0)


def _room_label(index):
    """How the game itself numbers a room.

    The tutorial stores each of its 19 puzzles twice -- the demonstration the game plays for
    you, then the same room to try -- so its labels carry which half of the pair a slot is.
    """
    if index < TUTORIAL_END:
        pair, half = divmod(index, 2)
        return f"tutorial {pair + 1}{'a' if half == 0 else 'b'}"
    if index < ADVANCED_START:
        floor, level = divmod(index - INTERMEDIATE_START, INTERMEDIATE_PER_FLOOR)
        return f"int {floor + 1}-{level + 1}"
    if index < PRO_START:
        floor, level = divmod(index - ADVANCED_START, ADVANCED_PER_FLOOR)
        return f"adv {floor + 1}-{level + 1}"
    return f"pro {index - PRO_START + 1}"


def _force_room(context):
    """Hook body: pin the room number on the way into LoadRoom, once.

    Writing it from outside on a frame boundary is not enough: the route into a room sets the
    number and calls the loader within the same frame. Hooking the loader's read of it puts
    the write between the two. It fires once and then stands down, so that clearing the room
    lets the cartridge advance to the next one of its own accord instead of being pinned into
    replaying this one.
    """
    pyboy_instance, room = context
    if room[0] is not None:
        pyboy_instance.memory[ROOM_NUMBER_ADDR] = room[0]
        room[0] = None


class GameWrapperAdventuresOfLolo(PyBoyGameWrapper):
    """
    This class wraps Adventures of Lolo, and provides easy access to the room, the hearts and
    Lolo himself for AIs.

    Every room is a puzzle: collect the heart framers, which opens the door, and walk into it.
    Emerald Framers can be pushed, enemies cannot be walked through, and a magic shot turns
    the enemy Lolo faces into an egg.

    Two things about the cartridge shape this wrapper. The board buffer in work RAM is the
    room *as it was loaded* and is never touched again, so the live position is read off the
    background tilemap instead and `game_area` is the two of them combined. And the cartridge
    ships eight terrain themes in which the same cell renders with different tiles, so
    `start_game` measures the handful of tile numbers it needs while the room is still fresh.

    Left alone the board is completely still: the enemies move only when Lolo does, which is
    what makes `GameWrapperAdventuresOfLolo.settle` work at all.

    If you call `print` on an instance of this object, it will show an overview of everything
    this object provides.
    """

    cartridge_title = "LOLO2"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`

    Floor is `1`, rock `2`, tree `3`, river `4`, bridge `5`, one-way pass `6`, Emerald Framer
    `7`, heart framer `8`, magic heart framer `9`, desert `10`, break tile `11`, flower bed
    `12`, marker `13`, the closed door `14`, the open door `15`, Lolo `16` and an enemy `17`.
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`

    Anything walkable is `0`, a wall `1`, an Emerald Framer `2`, a heart framer `3`, the
    closed door `4`, the open door `5`, Lolo `6` and an enemy `7`.
    """

    def __init__(self, *args, **kwargs):
        self.room = 0
        """The room index the loader was asked for, zero-based over all 163 slots"""
        self.floor = 0
        """The floor the cartridge says it is on"""
        self.level_in_floor = 0
        """Which level of that floor"""
        self.hearts_left = 0
        """Heart framers still to collect. The door opens when this reaches zero"""
        self.magic_shots = 0
        """Magic shots in hand: +2 for each magic heart framer collected, -1 for each shot"""
        self.lolo = (0.0, 0.0)
        """Where Lolo is, as ``(row, column)`` in half-cells. He really does stand on halves"""
        self.door = (0, 0)
        """Where the room's one door is, as ``(row, column)``"""
        self.life_lost = False
        """Whether Lolo has lost a life since the room was started or reset"""

        self._tile_heart = -1
        self._tile_framer = -1
        self._tile_door_closed = -1
        self._tile_door_open = -1
        self._forced_room = [None]
        self._hook_registered = False
        self._last_hearts = 0
        self._last_room = -1

        super().__init__(*args, game_area_section=(0, 0, ROOM_SIDE, ROOM_SIDE), game_area_follow_scxy=False, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.room = self.pyboy.memory[ROOM_NUMBER_ADDR]
        self.floor = self.pyboy.memory[FLOOR_ADDR]
        self.level_in_floor = self.pyboy.memory[LEVEL_IN_FLOOR_ADDR]
        self.hearts_left = self.pyboy.memory[HEARTS_LEFT_ADDR]
        self.magic_shots = self.pyboy.memory[MAGIC_SHOTS_ADDR]
        # Lolo is the first pair of sprites in the shadow OAM in every room measured, which is
        # what lets this be a two-byte read rather than a search of the buffer.
        buffer = self.pyboy.memory[OAM_BUFFER_ADDR : OAM_BUFFER_ADDR + 2]
        self.lolo = _cell_of(buffer[0], buffer[1])

        # Losing a life is not a flag anywhere in work RAM: the cartridge answers by putting
        # the room back the way it was, which gives the hearts already collected back. The
        # room number is what tells that apart from simply moving on to the next room.
        if self.pyboy.memory[SCENE_ADDR] == SCENE_PLAYING:
            if self.room == self._last_room and self.hearts_left > self._last_hearts:
                self.life_lost = True
            self._last_room = self.room
            self._last_hearts = self.hearts_left

    def _tilemap_cells(self):
        """The top-left tile of each cell's 2 by 2 block, as an 8 by 8.

        The playfield is background columns 1-16 and rows 1-16, so cell (r, c) starts at tile
        (1 + 2c, 1 + 2r). One tile per cell is enough: no two objects in a room share a
        top-left tile.
        """
        background = self.pyboy.tilemap_background
        return [[background[1 + 2 * col, 1 + 2 * row] for col in range(ROOM_SIDE)] for row in range(ROOM_SIDE)]

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            board = self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + ROOM_BYTES]
            tilemap = self._tilemap_cells()
            grid = []
            for row in range(ROOM_SIDE):
                line = []
                for col in range(ROOM_SIDE):
                    tile = tilemap[row][col]
                    code = board[row * ROOM_SIDE + col]
                    if code in (CODE_HEART, CODE_MAGIC_HEART):
                        # A heart framer never moves, so the only question is whether it is
                        # still there, and the tile answers that. Which of the two kinds it is
                        # comes from the loaded room, because both draw the same tile. An
                        # unknown tile means the room is reported as it was loaded.
                        line.append(code if self._tile_heart < 0 or tile == self._tile_heart else CODE_FLOOR)
                    elif code == CODE_DOOR:
                        # The door does not move either. It opens the frame the last heart is
                        # taken, and its open tile is the closed one plus two.
                        if self._tile_door_closed < 0 or tile == self._tile_door_closed:
                            line.append(CODE_DOOR)
                        elif tile == self._tile_door_open:
                            line.append(CODE_DOOR_OPEN)
                        else:
                            line.append(CODE_FLOOR)  # Lolo is standing in the doorway
                    elif self._tile_framer >= 0 and tile == self._tile_framer:
                        # An Emerald Framer is the one object that moves, so this is a search
                        # of the whole room rather than a check of where it was loaded.
                        line.append(CODE_FRAMER)
                    elif code == CODE_FRAMER:
                        # Pushed away from where it was loaded -- or, when the tile is unknown,
                        # still there, because nothing here can say that it moved.
                        line.append(CODE_FLOOR if self._tile_framer >= 0 else CODE_FRAMER)
                    elif code == CODE_LOLO or CODE_ENEMY_MIN <= code <= CODE_ENEMY_MAX:
                        line.append(CODE_FLOOR)  # Actors are sprites: the cell under them is floor
                    else:
                        line.append(code)
                grid.append(line)

            # Lolo and the enemies are drawn in from the sprites, which is the only thing that
            # says where they are now.
            for row, col in self.enemies():
                if 0 <= round(row) < ROOM_SIDE and 0 <= round(col) < ROOM_SIDE:
                    grid[round(row)][round(col)] = CODE_ENEMY
            row, col = self.lolo
            if 0 <= round(row) < ROOM_SIDE and 0 <= round(col) < ROOM_SIDE:
                grid[round(row)][round(col)] = CODE_LOLO

            self._cached_game_area_tiles = np.asarray(grid, dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the room as an 8 by 8 matrix of cell codes, as it is right now.

        The terrain comes from the room the loader built, everything that can be taken, pushed
        or opened comes from the background tilemap, and Lolo and the enemies are drawn in
        from the sprites. Lolo stands on half-cells, so his position is rounded here; read
        `GameWrapperAdventuresOfLolo.lolo` for the exact one.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the room
        """
        return self.mapping[self._game_area_tiles()]

    def enemies(self):
        """
        Return every enemy and egg on screen, as a list of ``(row, column)`` in half-cells.

        Every actor on this cartridge is drawn as two sprites side by side, filled into the
        shadow OAM in pairs: Lolo in slots 0 and 1, then one pair per enemy or egg. Only the
        left half of each pair is kept, which is what makes an enemy one cell rather than two.
        """
        buffer = self.pyboy.memory[OAM_BUFFER_ADDR : OAM_BUFFER_ADDR + OAM_BUFFER_BYTES]
        entries = [(buffer[i], buffer[i + 1]) for i in range(0, OAM_BUFFER_BYTES, 4) if buffer[i]]
        return sorted({_cell_of(y, x) for y, x in entries[2:][::2]})

    def hearts(self):
        """
        Return where the heart framers still on the board are, as a list of ``(row, column)``.
        """
        grid = self._game_area_tiles().tolist()
        return [
            (row, col)
            for row in range(ROOM_SIDE)
            for col in range(ROOM_SIDE)
            if grid[row][col] in (CODE_HEART, CODE_MAGIC_HEART)
        ]

    def framers(self):
        """
        Return where the Emerald Framers are now, as a list of ``(row, column)``.

        These are the blocks Lolo pushes, so they move, and the list is what is on the screen
        rather than what the room was loaded with.
        """
        grid = self._game_area_tiles().tolist()
        return [(row, col) for row in range(ROOM_SIDE) for col in range(ROOM_SIDE) if grid[row][col] == CODE_FRAMER]

    def rooms(self):
        """
        Return all 163 rooms, decoded straight out of the cartridge, as tuples of eight
        eight-character rows.

        This needs no emulation at all: the table is flat and uncompressed in ROM bank 13.
        It is also how a claim about a room can be settled without a screenshot.
        """
        return [self.room_layout(index) for index in range(ROOM_COUNT)]

    def room_layout(self, index):
        """
        Return one room as eight eight-character rows, decoded out of ROM bank 13.

        This is the room as the loader would build it, not the position on screen. Use
        `game_area` for that.

        Args:
            index (int): The room to read, 0-162
        """
        if not 0 <= index < ROOM_COUNT:
            raise PyBoyInvalidInputException(
                f"{index} is out of bounds. This cartridge has {ROOM_COUNT} rooms, so only values between 0 and "
                f"{ROOM_COUNT - 1} are allowed."
            )
        start = ROOM_TABLE_ADDR + index * ROOM_BYTES
        try:
            cells = self.pyboy.memory[ROOM_TABLE_BANK, start : start + ROOM_BYTES]
        except PyBoyOutOfBoundsException:
            raise PyBoyException(
                f"This ROM has no bank {ROOM_TABLE_BANK}, so it does not hold the room table. The rooms were read "
                "from the 256 KiB European release, whose internal title is LOLO2."
            ) from None
        return tuple(
            [
                "".join([CELL_GLYPHS.get(cells[row * ROOM_SIDE + col], "?") for col in range(ROOM_SIDE)])
                for row in range(ROOM_SIDE)
            ]
        )

    def room_label(self, index=None):
        """
        Return how the game itself numbers a room: `room_label(38)` is ``"int 1-1"``.

        Args:
            index (int): The room to name. Defaults to the one that is loaded
        """
        return _room_label(self.room if index is None else index)

    def _learn_tiles(self):
        """Measure this room's tile numbers for heart, Framer and door, while they still agree.

        Called on a freshly loaded room, when the board buffer and the tilemap describe the
        same thing: every heart cell still holds a heart, every Framer is where it was loaded,
        and the door is shut. The open-door tile cannot be read yet, because no room starts
        with it open, so it is taken as the closed tile plus two.

        An object the room does not contain simply stays unknown, which is not an error:
        plenty of rooms have no Framer, and six have no heart at all. An object whose tile
        turns out to be the floor's is treated as unknown too, because a tile that cannot be
        told from the floor cannot answer whether the object is still there, and the room as
        it was loaded is then the better answer of the two.
        """
        board = self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + ROOM_BYTES]
        tilemap = self._tilemap_cells()
        self._tile_heart = -1
        self._tile_framer = -1
        self._tile_door_closed = -1
        self._tile_door_open = -1
        floor = -1
        for row in range(ROOM_SIDE):
            for col in range(ROOM_SIDE):
                code = board[row * ROOM_SIDE + col]
                tile = tilemap[row][col]
                if code == CODE_FLOOR and floor < 0:
                    floor = tile
                elif code in (CODE_HEART, CODE_MAGIC_HEART) and self._tile_heart < 0:
                    self._tile_heart = tile
                elif code == CODE_FRAMER and self._tile_framer < 0:
                    self._tile_framer = tile
                elif code == CODE_DOOR and self._tile_door_closed < 0:
                    self._tile_door_closed = tile
                    self._tile_door_open = tile + 2
                    self.door = (row, col)
        if floor >= 0:
            if self._tile_heart == floor:
                self._tile_heart = -1
            if self._tile_framer == floor:
                self._tile_framer = -1
            if self._tile_door_closed == floor:
                self._tile_door_closed = -1
                self._tile_door_open = -1
        self._tile_cache_invalid = True

    def settle(self, max_ticks=SETTLE_MAX_TICKS, stable_ticks=SETTLE_STABLE_TICKS, min_ticks=SETTLE_MIN_TICKS):
        """
        Run the emulator until Lolo's move has finished, and report whether it did.

        What is watched is Lolo's own pair of sprites rather than the whole board, and that is
        the whole of this method. Watching the tilemap is wrong because it is updated the
        frame a heart is taken, so a move that ends on a heart would be called finished while
        Lolo is still sliding. Watching every sprite is wrong because six of the eight enemies
        patrol, and once Lolo's first move wakes them they never stop, so a rule that waits for
        the whole board to hold still cannot fire in those rooms at all.

        Lolo's own slide is the thing a move is actually waiting for, it always ends, and it
        ends in the same 17 or 18 frames in every room. `min_ticks` covers the magic shot,
        which leaves Lolo's sprite still and needs about eleven frames to fly and land.

        Args:
            max_ticks (int): Give up after this many frames
            stable_ticks (int): Frames Lolo's sprite must hold still
            min_ticks (int): The fewest frames to run, so a magic shot has time to land

        Returns
        -------
        bool:
            Whether the move finished within `max_ticks`
        """
        previous = None
        stable = 0
        for tick in range(max_ticks):
            self.pyboy.tick(1, False, False)
            current = self.pyboy.memory[OAM_BUFFER_ADDR : OAM_BUFFER_ADDR + LOLO_SPRITE_BYTES]
            if current == previous:
                stable += 1
                if stable >= stable_ticks and tick + 1 >= min_ticks:
                    return True
            else:
                previous = current
                stable = 0
        return False

    def set_room(self, index):
        """
        Select the room the cartridge's loader will build, zero-based over all 163 slots:
        `set_room(38)` is the first intermediate room. See `room_label` for how the game
        numbers them.

        This has to be called before `start_game`. The loader is hooked because the route into
        a room sets the room number and calls the loader inside one frame, and the hook stands
        down after it has fired once, so clearing the room lets the cartridge move on to the
        next one instead of replaying this one for ever.

        Args:
            index (int): The room to load, or `None` to take the one the boot route opens with
        """
        if index is not None and not 0 <= index < ROOM_COUNT:
            raise PyBoyInvalidInputException(
                f"{index} is out of bounds. This cartridge has {ROOM_COUNT} rooms, so only values between 0 and "
                f"{ROOM_COUNT - 1} are allowed."
            )
        self._forced_room[0] = index
        if index is not None and not self._hook_registered:
            self.pyboy.hook_register(ROM_BANK, LOAD_ROOM_READ, _force_room, (self.pyboy, self._forced_room))
            self._hook_registered = True

    def _is_playing(self):
        """Whether a graded room is up and waiting for input.

        Three things have to agree. The scene has to be the one the intermediate route runs
        in, because the tutorial's demonstration rooms play themselves and a board that moves
        on its own is worse than no board at all. The board buffer has to be non-empty,
        because it is zero on every menu. And Lolo has to have a sprite, because the buffer
        keeps the last room's bytes through the cutscene that precedes the first one.
        """
        return (
            self.pyboy.memory[SCENE_ADDR] == SCENE_PLAYING
            and any(self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + ROOM_BYTES])
            and self.pyboy.memory[OAM_BUFFER_ADDR] != 0
        )

    def _boot(self, story_presses):
        """Get from power-on to a graded room. `True` if one appeared.

        The route is: wait out the title, start for the NEW GAME wheel, A to choose it, then A
        through the King's introduction to the screen that offers ENTRY or INTERMEDIATE, B to
        take INTERMEDIATE, and A through the orchestra cutscene until a room is up.

        B rather than A at that one screen is the whole point. A starts the tutorial, where the
        first room of every pair is a demonstration the game plays for itself; B goes to the
        graded rooms, which is the only route that takes input.
        """
        self.pyboy.tick(BOOT_TITLE_TICKS, False, False)
        self.pyboy.button("start", 5)
        self.pyboy.tick(BOOT_MENU_TICKS, False, False)
        self.pyboy.button("a", 5)
        self.pyboy.tick(BOOT_MENU_TICKS, False, False)
        for _ in range(story_presses):
            self.pyboy.button("a", 4)
            self.pyboy.tick(BOOT_STORY_TICKS, False, False)
        self.pyboy.button("b", 6)
        self.pyboy.tick(BOOT_MENU_TICKS + 30, False, False)
        for _ in range(BOOT_MAX_ROOM_PRESSES):
            self.pyboy.button("a", 3)
            self.pyboy.tick(BOOT_ROOM_TICKS, False, False)
            if self._is_playing():
                return True
        return False

    def start_game(self, timer_div=None, room=None, magic_shots=0):
        """
        Call this function right after initializing PyBoy. This walks the title screen, the
        King's introduction and the cutscene, and gives back control on the first frame a room
        is up and listening.

        The state of the emulator is saved, and using `reset_game`, you can get back to this
        point of the game instantly.

        The boot is retried across a handful of tap counts rather than trusted once. The one
        screen where the route presses B instead of A is reached by counting taps through the
        King's introduction, and landing one screen early or late starts the tutorial instead,
        whose demonstration rooms play themselves.

        Booting straight into a room starts the magic-shot meter empty, because the meter is
        the player's and not the room's: on a real playthrough whatever was left over from the
        room before comes with you. Rooms that need a shot they cannot earn in-room are
        unclearable from a cold boot for that reason and not because anything is wrong. Pass
        `magic_shots` to play them.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            * room (int): Room to load, 0-162
            * magic_shots (int): Seed the magic-shot meter with this many shots
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset_game' instead.")

        if room is not None:
            self.set_room(room)
        wanted_room = self._forced_room[0]

        power_on = io.BytesIO()
        self.pyboy.save_state(power_on)
        for presses in BOOT_STORY_ALTERNATIVES:
            power_on.seek(0)
            self.pyboy.load_state(power_on)
            self.pyboy.tick(1, False, False)
            # Re-arm the hook: it stands down after firing, and every retry loads the room again.
            self._forced_room[0] = wanted_room
            if self._boot(presses):
                break
        else:
            raise PyBoyException("No room was reached while booting. Check that this is the right ROM revision.")

        self.settle()
        # Learned now, while the board buffer and the tilemap still describe the same room.
        self._learn_tiles()
        if magic_shots:
            self.pyboy.memory[MAGIC_SHOTS_ADDR] = magic_shots
        self.pyboy.tick(1, False, False)
        self.life_lost = False
        self._last_room = self.room
        self._last_hearts = self.hearts_left

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to put the room back
        the way the loader built it, hearts, Framers and enemies included.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self.life_lost = False
        self._last_room = self.room
        self._last_hearts = self.hearts_left

    def door_open(self):
        """
        Return whether the door has opened, which happens the frame the last heart is taken.
        """
        grid = self._game_area_tiles().tolist()
        return bool(grid[self.door[0]][self.door[1]] == CODE_DOOR_OPEN)

    def room_solved(self):
        """
        Return whether every heart framer has been collected and Lolo is standing on the door,
        which is how a room is won.
        """
        return self.hearts_left == 0 and (round(self.lolo[0]), round(self.lolo[1])) == tuple(self.door)

    def game_over(self):
        """
        Return whether Lolo has lost a life since the room was started or reset.

        The cartridge keeps no lives counter this wrapper can read, and it answers a death by
        restarting the room where Lolo stands, which is unmistakable from the outside: the
        hearts he had collected come back while the room number stays put. That is what this
        reports, and `reset_game` clears it.
        """
        return self.life_lost

    def __repr__(self):
        grid = self._game_area_tiles().tolist()
        lines = [
            "".join([CELL_GLYPHS.get(grid[row][col], "?") for col in range(ROOM_SIDE)]) for row in range(ROOM_SIDE)
        ]
        return (
            "Adventures of Lolo:\n"
            + f"Room: {self.room_label()} (index {self.room})\n"
            + f"Hearts left: {self.hearts_left}\n"
            + f"Magic shots: {self.magic_shots}\n"
            + f"Lolo: {self.lolo}\n"
            + f"Door: {self.door}{' (open)' if self.door_open() else ''}\n"
            + "Room:\n"
            + "\n".join(lines)
        )
