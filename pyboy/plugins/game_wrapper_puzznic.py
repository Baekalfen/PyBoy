#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperPuzznic.cartridge_title": False,
    "GameWrapperPuzznic.post_tick": False,
}

import io

import numpy as np

import pyboy
from pyboy.api.constants import TILES
from pyboy.utils import PyBoyException, PyBoyInvalidInputException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# The playfield. 12 rows of 10 cells, two bytes per cell, 20 bytes per row. Only the first
# byte of a cell carries the type; the second points at the block's record.
GRID_ADDR = 0xDF00
GRID_ROWS = 12
GRID_COLS = 10
CELL_STRIDE = 2
ROW_STRIDE = 20
GRID_BYTES = GRID_ROWS * ROW_STRIDE

CURSOR_COL_ADDR = 0xD012
CURSOR_ROW_ADDR = 0xD013
TOTAL_BLOCKS_ADDR = 0xD018  # Blocks the stage loaded with. Never decremented
BLOCKS_REMAINING_ADDR = 0xD019  # Decremented once per block removed
STAGE_INDEX_ADDR = 0xD003  # The stage the loader will build
STAGE_LOADER_ENTRY = 0x0430  # Bank 0. Reads STAGE_INDEX_ADDR a few instructions in

# Cell types. Only CELL_EMPTY lets a block move into it; the rest obstruct.
CELL_EMPTY = 0x00
CELL_CLEARING = 0x01  # Transient: a block is being removed, or is in motion
CELL_LEDGE = 0x02
CELL_OUTSIDE = 0x03
CELL_WALL = 0x06
BLOCK_MIN = 0x08  # 0x08-0x0F are blocks. The type is the value minus BLOCK_TYPE_OFFSET
BLOCK_MAX = 0x0F
BLOCK_TYPE_OFFSET = 7

CELL_GLYPHS = {CELL_EMPTY: ".", CELL_CLEARING: "*", CELL_LEDGE: "=", CELL_OUTSIDE: " ", CELL_WALL: "#"}

# The title menu and the password screen are sprites, so both can be read back. The
# coordinates below are the ones in the OAM DMA buffer, which the cartridge keeps at 0xC000
# and copies to hardware OAM every frame. They are 16 pixels below and 8 to the right of
# where `pyboy.api.sprite.Sprite` reports them, which is why they are read from the buffer.
OAM_BUFFER_ADDR = 0xC000
OAM_BUFFER_BYTES = 160
MENU_ARROW_TILE = 0xAC
MENU_ENTRIES = {"1player": 88, "2players": 104, "password": 120}
MENU_PRESS_TICKS = 8
MENU_GAP_TICKS = 26
TITLE_MAX_TICKS = 900

# Every round has a password, and the table is in the cartridge: 128 ten-byte entries at
# 0x47FA in ROM bank 1. Eight bytes are the password in the game's own text encoding, the
# ninth is the round number and the tenth is a check byte.
PASSWORD_TABLE_BANK = 1
PASSWORD_TABLE_ADDR = 0x47FA
PASSWORD_LENGTH = 8
PASSWORD_STRIDE = 10
PASSWORD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ."
TEXT_LETTER_BASE = 0x0A  # 'A' in the game's text encoding, so 0x00-0x09 are the digits
TEXT_PERIOD = 0x24  # '.' as the ROM stores it
TILE_PERIOD = 0x8B  # '.' as the screen shows it
SLOT_Y = 48
SLOT_X = (24, 40, 56, 72, 96, 112, 128, 144)
EMPTY_SLOT_TILE = 0x8C
ENTRY_ORIGIN = (80, 16)  # Where the arrow sits for the cell holding 'A'
ENTRY_PITCH = 16
END_CELL = (3, 6)  # The bottom row is NEXT (3,0), BACK (3,3), END (3,6)

# Waiting for the cartridge. A push is not instantaneous: the block slides, blocks above it
# fall, matches clear through a CELL_CLEARING transient, and the fall can cascade.
SETTLE_MAX_TICKS = 600
SETTLE_STABLE_TICKS = 4  # Frames the grid must hold still to count as settled
BOOT_MAX_TICKS = 1800
BOOT_PRESS_EVERY = 12
INTRO_MAX_TICKS = 900  # A stage is readable while its intro still ignores every button
INTRO_STEP_TICKS = 30
INTRO_PRESS_TICKS = 6

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
mapping_compressed[CELL_CLEARING] = 1
mapping_compressed[CELL_LEDGE] = 2
mapping_compressed[CELL_WALL] = 3
for _type, _cell in enumerate(range(BLOCK_MIN, BLOCK_MAX + 1)):
    mapping_compressed[_cell] = 4 + _type
"""
Compressed mapping for `pyboy.PyBoy.game_area_mapping`
"""

mapping_minimal = np.zeros(TILES, dtype=np.uint8)
mapping_minimal[CELL_LEDGE] = 1
mapping_minimal[CELL_WALL] = 1
mapping_minimal[CELL_CLEARING] = 2
mapping_minimal[BLOCK_MIN : BLOCK_MAX + 1] = 2
"""
Minimal mapping for `pyboy.PyBoy.game_area_mapping`
"""


def _decode_text(byte):
    """One byte of the game's text encoding, as a character."""
    if TEXT_LETTER_BASE <= byte < TEXT_LETTER_BASE + 26:
        return chr(ord("A") + byte - TEXT_LETTER_BASE)
    if byte < TEXT_LETTER_BASE:
        return str(byte)
    if byte in (TEXT_PERIOD, TILE_PERIOD):
        return "."
    return None


def _force_stage(context):
    """Hook body: pin the stage index on the way into the stage loader.

    Writing it from outside on a frame boundary is not enough. A title screen can reset the
    index and call the loader within the same frame, and the loader wins. Hooking its entry
    puts the write between the reset and the read.
    """
    pyboy_instance, stage_index = context
    if stage_index[0] is not None:
        pyboy_instance.memory[STAGE_INDEX_ADDR] = stage_index[0]


class GameWrapperPuzznic(PyBoyGameWrapper):
    """
    This class wraps Puzznic, and provides easy access to the playfield, the cursor and the
    block counters for AIs.

    Puzznic is a puzzle game: the cursor picks a block up and slides it sideways, and two
    blocks of the same type vanish when they touch. A stage is cleared when every block is
    gone.

    The playfield lives in work RAM rather than in the tilemap, so `game_area` is read from
    there. The values are the cartridge's own cell types, which carry more than the screen
    does: a block in motion reads as ``1`` for the frames it is clearing or falling.

    If you call `print` on an instance of this object, it will show an overview of
    everything this object provides.
    """

    cartridge_title = "PUZZNIC"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`

    Empty cells are `0`, a block being cleared is `1`, a ledge is `2`, a wall is `3`, and
    the eight block types are `4` to `11`.
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`

    Empty cells are `0`, anything solid is `1`, and every block is `2`.
    """

    def __init__(self, *args, **kwargs):
        self.stage = 0
        """The stage index the cartridge's loader built, zero-based"""
        self.blocks_total = 0
        """The number of blocks this stage loaded with"""
        self.blocks_remaining = 0
        """The number of blocks still on the playfield"""
        self.blocks_cleared = 0
        """The number of blocks matched away so far. Can be used for AI scoring"""
        self.cursor = (0, 0)
        """The cursor's position on the playfield, as a tuple of ``(row, column)``"""

        self._forced_stage = [None]
        self._hook_registered = False

        super().__init__(*args, game_area_section=(0, 0, GRID_COLS, GRID_ROWS), game_area_follow_scxy=False, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.stage = self.pyboy.memory[STAGE_INDEX_ADDR]
        self.blocks_total = self.pyboy.memory[TOTAL_BLOCKS_ADDR]
        self.blocks_remaining = self.pyboy.memory[BLOCKS_REMAINING_ADDR]
        self.blocks_cleared = self.blocks_total - self.blocks_remaining
        self.cursor = (self.pyboy.memory[CURSOR_ROW_ADDR], self.pyboy.memory[CURSOR_COL_ADDR])

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            raw = self.pyboy.memory[GRID_ADDR : GRID_ADDR + GRID_BYTES]
            self._cached_game_area_tiles = np.asarray(
                [[raw[ROW_STRIDE * row + CELL_STRIDE * col] for col in range(GRID_COLS)] for row in range(GRID_ROWS)],
                dtype=np.uint32,
            )
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the 12 by 10 playfield as a matrix of the cartridge's cell types.

        The cursor, the block counters and the blocks themselves are available as attributes
        and methods of this class.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the playfield
        """
        # Sprites are deliberately not drawn in: the blocks are not sprites, and the one
        # thing that is -- the cursor -- has its own attribute read from work RAM.
        return self.mapping[self._game_area_tiles()]

    def blocks(self):
        """
        Return every block on the playfield as a list of ``(row, column, type)``.

        A block in motion is not in the list: the cell it is leaving reads as clearing until
        it lands. Wait for the board to settle before reading it, or use `game_area`.
        """
        raw = self.pyboy.memory[GRID_ADDR : GRID_ADDR + GRID_BYTES]
        blocks = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                value = raw[ROW_STRIDE * row + CELL_STRIDE * col]
                if BLOCK_MIN <= value <= BLOCK_MAX:
                    blocks.append((row, col, value - BLOCK_TYPE_OFFSET))
        return blocks

    def block_counts(self):
        """
        Return how many blocks of each type are left, as a dict of ``{type: count}``.

        Matching is pairwise, so a type down to a single block can never be removed again.
        """
        counts = {}
        for _row, _col, block_type in self.blocks():
            counts[block_type] = counts.get(block_type, 0) + 1
        return counts

    def passwords(self):
        """
        Return the round passwords, read out of the cartridge.

        The table is walked until an entry stops being a password whose round number follows
        the last one, which both finds the end of the table and checks the parse as it goes.
        The list is round-ordered, so index 0 is round 1.
        """
        passwords = []
        offset = PASSWORD_TABLE_ADDR
        expected = 1
        while offset + PASSWORD_STRIDE <= 0x8000:
            entry = self.pyboy.memory[PASSWORD_TABLE_BANK, offset : offset + PASSWORD_STRIDE]
            text = [_decode_text(byte) for byte in entry[:PASSWORD_LENGTH]]
            if entry[PASSWORD_LENGTH] != expected & 0xFF or any([character is None for character in text]):
                break
            passwords.append("".join(text))
            offset += PASSWORD_STRIDE
            expected += 1
        return passwords

    def _shadow_oam(self):
        """The OAM DMA buffer as ``(y, x, tile)`` for every visible sprite.

        Read from the buffer rather than through `pyboy.PyBoy.get_sprite`, because the menu
        coordinates above were measured here: the buffer holds the raw OAM values, 16 pixels
        below and 8 to the right of the screen coordinates a `pyboy.api.sprite.Sprite` gives.
        """
        buffer = self.pyboy.memory[OAM_BUFFER_ADDR : OAM_BUFFER_ADDR + OAM_BUFFER_BYTES]
        return [(buffer[i], buffer[i + 1], buffer[i + 2]) for i in range(0, OAM_BUFFER_BYTES, 4) if buffer[i]]

    def _menu_cursor(self):
        """Which title-menu entry is selected, or `None` when the menu is not up."""
        for y, _x, tile in self._shadow_oam():
            if tile == MENU_ARROW_TILE:
                for name, row in MENU_ENTRIES.items():
                    if y == row:
                        return name
        return None

    def _entry_cursor(self):
        """Which character cell the password screen's cursor is on, as ``(row, column)``."""
        for y, x, tile in self._shadow_oam():
            if tile == MENU_ARROW_TILE:
                return ((y - ENTRY_ORIGIN[0]) // ENTRY_PITCH, (x - ENTRY_ORIGIN[1]) // ENTRY_PITCH)
        return None

    def _entered_password(self):
        """What the password screen currently shows, with ``-`` for an empty slot."""
        filled = {x: tile for y, x, tile in self._shadow_oam() if y == SLOT_Y}
        return "".join(
            "-" if filled.get(x, EMPTY_SLOT_TILE) == EMPTY_SLOT_TILE else _decode_text(filled[x]) or "?" for x in SLOT_X
        )

    def _tap(self, button, hold=MENU_PRESS_TICKS, gap=MENU_GAP_TICKS):
        self.pyboy.button(button, hold)
        self.pyboy.tick(gap, False, False)

    def _wait_for_title(self):
        """Tick until the title menu is up. `True` if it appeared."""
        for _ in range(0, TITLE_MAX_TICKS, 30):
            if self._menu_cursor() is not None:
                return True
            self.pyboy.tick(30, False, False)
        return self._menu_cursor() is not None

    def _select_menu_entry(self, entry):
        """Move the title-menu cursor onto `entry` and press start."""
        for _ in range(len(MENU_ENTRIES) * 3):
            here = self._menu_cursor()
            if here is None:
                return False
            if here == entry:
                self._tap("start")
                return True
            self._tap("down")
        return False

    def _steer_entry_cursor(self, target, budget=32):
        """Walk the password screen's cursor onto `target`, checking it after every press."""
        for _ in range(budget):
            here = self._entry_cursor()
            if here is None:
                return False
            if here == target:
                return True
            if here[0] != target[0]:
                self._tap("down" if target[0] > here[0] else "up")
            else:
                self._tap("right" if target[1] > here[1] else "left")
            if self._entry_cursor() == here:
                return False  # The press did nothing, so the screen is not listening
        return False

    def _enter_password(self, password, attempts=3):
        """Type `password` on the password screen and confirm it with END.

        Every keystroke is checked against the slot it was meant to fill, and retried when it
        did not land. The screen drops a press now and again, and a password that is one
        character short is silently the wrong round rather than an error.
        """
        cells = {character: (i // 9, i % 9) for i, character in enumerate(PASSWORD_ALPHABET)}
        for index, character in enumerate(password):
            if character not in cells:
                raise PyBoyInvalidInputException(f"{character!r} is not on the password screen")
            for _ in range(attempts):
                if not self._steer_entry_cursor(cells[character]):
                    return False
                self._tap("a")
                if self._entered_password()[index] == character:
                    break
            else:
                return False
        if self._entered_password() != password:
            return False
        if not self._steer_entry_cursor(END_CELL):
            return False
        self._tap("a")
        return True

    def _stage_is_loaded(self):
        """`True` once a stage sits on the playfield with nothing cleared from it yet."""
        total = self.pyboy.memory[TOTAL_BLOCKS_ADDR]
        if total == 0 or self.pyboy.memory[BLOCKS_REMAINING_ADDR] != total:
            return False
        raw = self.pyboy.memory[GRID_ADDR : GRID_ADDR + GRID_BYTES]
        cells = raw[::CELL_STRIDE]
        if any(value == CELL_CLEARING for value in cells):
            return False
        return sum(1 for value in cells if BLOCK_MIN <= value <= BLOCK_MAX) == total

    def _wait_until_interactive(self):
        """Advance past the round's intro, and report how many frames it took.

        The stage loader fills work RAM before the round has finished announcing itself, so
        the board is fully readable while every button is still ignored -- about 200 frames.
        A game started in that window looks normal and answers nothing, which is the worst
        way for this to go wrong.

        Rather than hard-code the delay, this presses a direction from a save state at
        increasing offsets until the cursor answers, then rewinds and replays only the
        waiting, so the cursor is left exactly where the loader put it.
        """
        start = io.BytesIO()
        self.pyboy.save_state(start)

        def cursor():
            return (self.pyboy.memory[CURSOR_ROW_ADDR], self.pyboy.memory[CURSOR_COL_ADDR])

        def rewind(waited):
            start.seek(0)
            self.pyboy.load_state(start)
            if waited:
                self.pyboy.tick(waited, False, False)

        for waited in range(0, INTRO_MAX_TICKS, INTRO_STEP_TICKS):
            for direction in ("right", "left", "down", "up"):
                rewind(waited)
                before = cursor()
                self.pyboy.button(direction, INTRO_PRESS_TICKS)
                self.pyboy.tick(INTRO_PRESS_TICKS + 12, False, False)
                if cursor() != before:
                    rewind(waited)
                    return waited
        rewind(0)
        return None

    def settle(self, max_ticks=SETTLE_MAX_TICKS, stable_ticks=SETTLE_STABLE_TICKS):
        """
        Run the emulator until the playfield stops moving, and report whether it did.

        A push is not instantaneous: the block slides, the blocks above it fall, matches clear
        through a transient and the fall can cascade. Reading the board straight after a
        button press reads the middle of that. The board counts as settled once no cell is
        mid-clear and the grid has been identical for `stable_ticks` frames.

        Clearing the last block ends the stage and the cartridge loads the next round over the
        top of it, so this returns the moment the last block goes: that is the last moment
        this stage can be read at all.

        Args:
            max_ticks (int): Give up after this many frames
            stable_ticks (int): Frames the playfield must hold still

        Returns
        -------
        bool:
            Whether the playfield settled within `max_ticks`
        """
        total = self.pyboy.memory[TOTAL_BLOCKS_ADDR]
        previous = None
        stable = 0
        for _ in range(max_ticks):
            self.pyboy.tick(1, False, False)
            if self.pyboy.memory[TOTAL_BLOCKS_ADDR] != total:
                return False  # A new stage loaded, so there is nothing left to wait for
            if total and self.pyboy.memory[BLOCKS_REMAINING_ADDR] == 0:
                return True
            raw = self.pyboy.memory[GRID_ADDR : GRID_ADDR + GRID_BYTES]
            if any(value == CELL_CLEARING for value in raw[::CELL_STRIDE]):
                previous = raw
                stable = 0
                continue
            if raw == previous:
                stable += 1
                if stable >= stable_ticks:
                    return True
            else:
                previous = raw
                stable = 0
        return False

    def set_stage(self, index):
        """
        Select the stage the cartridge's loader will build, zero-based: `set_stage(3)` is
        round 4.

        This has to be called before `start_game`. The loader is hooked, and the index is
        written as it arrives, because writing it from outside on a frame boundary is not
        enough: a title screen resets the index and calls the loader within the same frame.

        Note that this swaps the layout under a game that still believes it is on round one.
        Passing `password` to `start_game` instead reaches the round the way a player would,
        with everything else on the cartridge set up the way it expects.

        Args:
            index (int): The stage to load, or `None` to leave the cartridge alone
        """
        self._forced_stage[0] = index
        if index is not None and not self._hook_registered:
            self.pyboy.hook_register(0, STAGE_LOADER_ENTRY, _force_stage, (self.pyboy, self._forced_stage))
            self._hook_registered = True

    def start_game(self, timer_div=None, stage=None, password=None):
        """
        Call this function right after initializing PyBoy. This navigates the title screen and
        gives back control on the first frame the cursor answers a button.

        The state of the emulator is saved, and using `reset_game`, you can get back to this
        point of the game instantly.

        A round can be reached in two ways. `password` types the round's password on the
        title screen's PASSWORD entry, which is the route a player would take and the one that
        leaves the rest of the cartridge's state consistent. `stage` pokes the stage loader
        instead, which is quicker and works on a dump with no usable menu.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            * stage (int): Stage index to force on the loader, zero-based
            * password (str): Password to type on the title screen, eight characters
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset_game' instead.")

        if stage is not None:
            self.set_stage(stage)

        title = self._wait_for_title()
        if title and password is not None:
            if not self._select_menu_entry("password"):
                raise PyBoyException("Couldn't select PASSWORD on the title menu")
            self.pyboy.tick(90, False, False)
            if not self._enter_password(password):
                raise PyBoyException(f"Couldn't type the password {password!r} on the password screen")
        elif title:
            if not self._select_menu_entry("1player"):
                raise PyBoyException("Couldn't select 1PLAYER on the title menu")

        for frame in range(0, BOOT_MAX_TICKS, BOOT_PRESS_EVERY):
            if not title:
                # No title menu on this dump, so tap through whatever is on screen instead.
                self.pyboy.button("start" if (frame // BOOT_PRESS_EVERY) % 2 == 0 else "a", 4)
            self.pyboy.tick(BOOT_PRESS_EVERY, False, False)
            if self._stage_is_loaded():
                break
        else:
            raise PyBoyException(f"No stage was loaded within {BOOT_MAX_TICKS} frames of booting")

        self.settle()
        if self._wait_until_interactive() is None:
            raise PyBoyException(
                "The stage loaded, but never accepted a button press. The board is readable "
                "during the round intro, so this usually means the intro is longer than "
                "expected, or the game is paused."
            )
        # Settle again. The intro is not only a wait: a round whose layout starts with
        # unsupported blocks drops them as it begins, and the frame the cursor first answers
        # on can be in the middle of that fall.
        self.settle()

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game
        back to the first playable frame of the stage `start_game` reached.

        To play a different round, reset the emulator and pass `stage` or `password` to
        `start_game` again.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

    def stage_cleared(self):
        """
        Return whether every block has been matched away, which is how a stage is won.
        """
        return self.blocks_total > 0 and self.blocks_remaining == 0

    def game_over(self):
        """
        Return whether the stage can no longer be cleared.

        Blocks are matched in pairs, so a type down to a single block is stuck there, and the
        stage is lost however much time is left on it. That is what this reports: it is a
        property of the position rather than a flag the cartridge sets, and it is the loss an
        AI can act on. A stage that runs out of time is reloaded by the cartridge, which shows
        up here as the counters going back to their starting values.
        """
        return 1 in set(self.block_counts().values())

    def __repr__(self):
        grid = self._game_area_tiles().tolist()
        lines = []
        for row in range(GRID_ROWS):
            line = []
            for col in range(GRID_COLS):
                value = int(grid[row][col])
                glyph = CELL_GLYPHS.get(value, str(value - BLOCK_TYPE_OFFSET) if value >= BLOCK_MIN else "?")
                if (row, col) == tuple(self.cursor):
                    glyph = "c" if value == CELL_EMPTY else "C"
                line.append(glyph)
            lines.append("".join(line))
        return (
            "Puzznic:\n"
            + f"Stage: {self.stage}\n"
            + f"Blocks: {self.blocks_remaining}/{self.blocks_total}\n"
            + f"Blocks cleared: {self.blocks_cleared}\n"
            + f"Cursor: {self.cursor}\n"
            + "Playfield:\n"
            + "\n".join(lines)
        )
