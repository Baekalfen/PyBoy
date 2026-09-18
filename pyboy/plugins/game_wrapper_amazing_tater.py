#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperAmazingTater.cartridge_title": False,
    "GameWrapperAmazingTater.post_tick": False,
}

import io

import numpy as np

import pyboy
from pyboy.api.constants import TILES
from pyboy.utils import PyBoyException, PyBoyInvalidInputException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# The composed board. LoadLevel builds a 20 by 18 map of cell codes here, one byte per cell,
# and the whole game runs on it: walls, pits, blocks, turnstiles, the taters and the exit
# flag are all in it, and each code carries the shape information a bot needs.
BOARD_ADDR = 0xC2F2
BOARD_COLS = 20
BOARD_ROWS = 18
ROW_STRIDE = 20  # Not the hardware tilemap's 32
BOARD_BYTES = BOARD_ROWS * ROW_STRIDE

BOARD_WIDTH_ADDR = 0xC2BD  # The room's width plus its border, so W + 2
BOARD_HEIGHT_ADDR = 0xC2BE  # ... and H + 2
BOARD_X_OFFSET_ADDR = 0xC2BF  # Where the bordered box sits in the 20 by 18 buffer
BOARD_Y_OFFSET_ADDR = 0xC2C0

GAME_MODE_ADDR = 0xC131  # 0 PUZZLE, 1/2 PRACTICE, 3 BEGINNER and ACTION
OVERLAY_ADDR = 0xC2AC  # 0 while the room is being played, non-zero under a menu
TATERS_ON_BOARD_ADDR = 0xC2AD  # One bit per character still to reach the flag
ACTIVE_TATER_ADDR = 0xC2AE  # Which one select has the controls on
MENU_CURSOR_ADDR = 0xD37D  # SELECT MODE highlight, 0-3. 0x80 anywhere else

LOAD_LEVEL = 0x08C0  # Bank 0. Entered with HL holding twice the level index

# The cell codes. Every one was matched against the rendered screen and, for the shapes,
# against the cartridge's own 15-entry shape table.
CODE_FLOOR = 0x00
CODE_PIT = 0xE0
CODE_OUTSIDE = 0xFF
BLOCK_MIN, BLOCK_MAX = 0x40, 0x4F  # 0x40 | mask of which neighbours share the block
SETTLED_MIN, SETTLED_MAX = 0x50, 0x5F  # The same, for a square that is over a pit
ARM_MIN, ARM_MAX = 0x80, 0x83  # 0x80 | direction from the pivot: up right down left
ARM_PIT_MIN, ARM_PIT_MAX = 0x90, 0x93
PIVOT_MIN, PIVOT_MAX = 0xA0, 0xAE  # 0xA0 | index into the shape table
TATER_MIN, TATER_MAX = 0xC0, 0xC3  # 0xC0 | which of the four characters
EXIT_CODE = 0xD0  # Every room on the cartridge has exactly one flag
WALL_MIN, WALL_MAX = 0xF0, 0xFE  # Fifteen wall graphics. All of them are just wall

# The 15-byte table at 0x0BF6. The high nibble of entry `i` is the arm mask of the pivot
# whose code is 0xA0 + i, with bit 8 up, 4 right, 2 down and 1 left.
SHAPE_TABLE_ADDR = 0x0BF6
SHAPE_TABLE_ENTRIES = 15
ROM_BANK = 0

# Three sets of rooms on the cartridge, and two of them are rooms. Set B, behind PRACTICE
# MODE, is a timed climb through ten floors whose board buffer holds the corridors of the
# neighbouring floors as well as the room, and whose tater starts outside the room: a
# different game rather than a different level, so this wrapper does not offer it.
# `(letter, the game mode that reaches the set, how many rooms)`, in index order.
LEVEL_SETS = (("A", 0, 41), ("C", 3, 64))
LEVEL_COUNT = 105

# How far down SELECT MODE each game mode sits. The menu reads BEGINNER, PUZZLE, PRACTICE,
# ACTION, and BEGINNER and ACTION both land on set C; this takes BEGINNER, which is the
# entry the cursor already starts on.
MODE_MENU_ROW = {0: 1, 1: 2, 3: 0}

# Room sizes the cartridge actually ships: 7x3 at the smallest, 18x16 at the largest. Used
# to tell a composed board from whatever the dimension bytes hold on a menu screen.
MIN_ROOM, MAX_ROOM = 3, 18

SETTLE_MAX_TICKS = 180  # A move's board writes span sixteen frames at the longest
SETTLE_STABLE_TICKS = 20  # Measured: the longest still spell inside an unfinished move is
# eight frames, when a block is dissolving into a pit
PRESS_TICKS = 5  # Frames a d-pad press is held
SWITCH_LOCKOUT_TICKS = 48  # Measured: after select the cartridge ignores the next press for
# 33 frames, and nothing on the board moves to say so
BOOT_MAX_TICKS = 6000  # The title screen alone runs about 400 frames, and BEGINNER MODE
# opens with a tutor who has several screens to say
BOOT_PRESS_TICKS = 5
BOOT_STEP_TICKS = 30
INTRO_MAX_TICKS = 300
INTRO_STEP_TICKS = 20
INTRO_FALLBACK_TICKS = 120

SWITCH_BUTTON = "select"
DIRECTIONS = ("up", "right", "down", "left")

CELL_GLYPHS = {CODE_OUTSIDE: " ", CODE_FLOOR: ".", CODE_PIT: "v", EXIT_CODE: "X"}
for _code in range(WALL_MIN, WALL_MAX + 1):
    CELL_GLYPHS[_code] = "#"
for _code in range(PIVOT_MIN, PIVOT_MAX + 1):
    CELL_GLYPHS[_code] = "@"
for _code in range(BLOCK_MIN, BLOCK_MAX + 1):
    CELL_GLYPHS[_code] = "$"
for _code in range(SETTLED_MIN, SETTLED_MAX + 1):
    CELL_GLYPHS[_code] = "%"
for _code in range(ARM_MIN, ARM_MAX + 1):
    CELL_GLYPHS[_code] = "+"
for _code in range(ARM_PIT_MIN, ARM_PIT_MAX + 1):
    CELL_GLYPHS[_code] = "-"
for _code in range(TATER_MIN, TATER_MAX + 1):
    CELL_GLYPHS[_code] = str(_code - TATER_MIN + 1)

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
mapping_compressed[CODE_FLOOR] = 1
mapping_compressed[WALL_MIN : WALL_MAX + 1] = 2
mapping_compressed[CODE_PIT] = 3
mapping_compressed[BLOCK_MIN : BLOCK_MAX + 1] = 4
mapping_compressed[SETTLED_MIN : SETTLED_MAX + 1] = 5
mapping_compressed[ARM_MIN : ARM_MAX + 1] = 6
mapping_compressed[ARM_PIT_MIN : ARM_PIT_MAX + 1] = 7
mapping_compressed[PIVOT_MIN : PIVOT_MAX + 1] = 8
mapping_compressed[EXIT_CODE] = 9
for _offset in range(TATER_MIN, TATER_MAX + 1):
    mapping_compressed[_offset] = 10 + _offset - TATER_MIN
"""
Compressed mapping for `pyboy.PyBoy.game_area_mapping`
"""

mapping_minimal = np.zeros(TILES, dtype=np.uint8)
mapping_minimal[CODE_OUTSIDE] = 1
mapping_minimal[WALL_MIN : WALL_MAX + 1] = 1
mapping_minimal[CODE_PIT] = 2
mapping_minimal[BLOCK_MIN : BLOCK_MAX + 1] = 3
mapping_minimal[SETTLED_MIN : SETTLED_MAX + 1] = 3
mapping_minimal[ARM_MIN : ARM_MAX + 1] = 4
mapping_minimal[ARM_PIT_MIN : ARM_PIT_MAX + 1] = 4
mapping_minimal[PIVOT_MIN : PIVOT_MAX + 1] = 4
mapping_minimal[TATER_MIN : TATER_MAX + 1] = 5
mapping_minimal[EXIT_CODE] = 6
"""
Minimal mapping for `pyboy.PyBoy.game_area_mapping`
"""


def _within_set(index):
    """``(letter, index inside that set, the game mode that reaches it)`` for a room index."""
    start = 0
    for letter, mode, size in LEVEL_SETS:
        if index < start + size:
            return letter, index - start, mode
        start += size
    raise PyBoyInvalidInputException(
        f"{index} is out of bounds. This wrapper offers {LEVEL_COUNT} rooms, so only values between 0 and "
        f"{LEVEL_COUNT - 1} are allowed."
    )


def _force_level(context):
    """Hook body: write HL on the way into LoadLevel.

    The loader is entered with HL holding twice the level index, worked out by its caller from
    a stage counter and a level-within-stage counter that between them do not cover a set
    evenly: set A's last room is the one left over after four stages of ten. Writing the index
    the loader is about to use sidesteps all of that, and it is the only write: the game mode
    still comes from the menu, so the cartridge stays in a state it put itself in.
    """
    pyboy_instance, level = context
    if level[0] is not None:
        pyboy_instance.register_file.HL = level[0] * 2


class GameWrapperAmazingTater(PyBoyGameWrapper):
    """
    This class wraps Amazing Tater, and provides easy access to the board, the characters and
    the level loader for AIs.

    Amazing Tater is a sokoban-like puzzle: one to four taters have to be walked to the exit
    flag, shoving blocks into pits and turning turnstiles out of the way to get there. The
    cartridge composes the whole room -- terrain, blocks, turnstiles, characters and the flag
    -- into a 20 by 18 map of cell codes in work RAM, so `game_area` is read from there rather
    than from the tilemap. The codes carry more than the screen does: a block square says
    which of its neighbours belong to the same block, and a turnstile pivot says which arms it
    has.

    If you call `print` on an instance of this object, it will show an overview of everything
    this object provides.
    """

    cartridge_title = "AMAZING-TATER"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`

    Outside the room is `0`, floor `1`, wall `2`, pit `3`, block `4`, block over a pit `5`,
    turnstile arm `6`, arm over a pit `7`, turnstile pivot `8`, the exit flag `9`, and the
    four taters `10` to `13`.
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`

    Floor is `0`, anything solid `1`, a pit `2`, a block `3`, any part of a turnstile `4`, a
    tater `5` and the exit flag `6`.
    """

    def __init__(self, *args, **kwargs):
        self.level = 0
        """The room index this wrapper asked the loader for, zero-based over set A then set C"""
        self.taters_left = 0
        """How many characters still have to reach the exit flag"""
        self.taters_home = 0
        """How many characters have reached the exit flag. Can be used for AI scoring"""
        self.taters_total = 0
        """How many characters the room started with"""
        self.active_tater = 0
        """Which character the controls are on, zero-based. Select hands them to the next one"""
        self.room_size = (0, 0)
        """The room's own width and height, without its border"""

        self._forced_level = [None]
        self._hook_registered = False

        super().__init__(*args, game_area_section=(0, 0, BOARD_COLS, BOARD_ROWS), game_area_follow_scxy=False, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        on_board = self.pyboy.memory[TATERS_ON_BOARD_ADDR]
        self.taters_left = bin(on_board).count("1")
        # A new room always loads with at least as many characters as the last one had left,
        # so this catches the cartridge moving on without being asked.
        if self.taters_left > self.taters_total:
            self.taters_total = self.taters_left
        self.taters_home = self.taters_total - self.taters_left
        self.active_tater = self.pyboy.memory[ACTIVE_TATER_ADDR]
        self.room_size = (self.pyboy.memory[BOARD_WIDTH_ADDR] - 2, self.pyboy.memory[BOARD_HEIGHT_ADDR] - 2)

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            raw = self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + BOARD_BYTES]
            self._cached_game_area_tiles = np.asarray(
                [[raw[ROW_STRIDE * row + col] for col in range(BOARD_COLS)] for row in range(BOARD_ROWS)],
                dtype=np.uint32,
            )
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the 18 by 20 board as a matrix of the cartridge's cell codes.

        The board is the whole room, cropped by nothing: cells outside the room read as
        `0xFF`, or as `0` through `GameWrapperAmazingTater.mapping_compressed`.

        A tater in mid-step is taken off the board and drawn as a sprite until it arrives, so
        for a dozen frames after every press there is no tater in the matrix at all. Call
        `GameWrapperAmazingTater.settle` first, or read
        `GameWrapperAmazingTater.taters_left`, which keeps counting through the step.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the board
        """
        return self.mapping[self._game_area_tiles()]

    def _find(self, low, high):
        raw = self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + BOARD_BYTES]
        return [
            (index // ROW_STRIDE, index % ROW_STRIDE, code) for index, code in enumerate(raw) if low <= code <= high
        ]

    def taters(self):
        """
        Return the characters still on the board, as a dict of ``{character: (row, column)}``.

        A character that has reached the flag is gone from the board, and so is one in
        mid-step. `GameWrapperAmazingTater.taters_left` is the count that keeps its value
        through a step.
        """
        return {code - TATER_MIN: (row, col) for row, col, code in self._find(TATER_MIN, TATER_MAX)}

    def blocks(self):
        """
        Return every block square as a list of ``(row, column, settled)``.

        `settled` is `True` for a square that has been shoved onto a pit and filled it. A
        block is made of one or more squares, and its code says which of its neighbours belong
        to the same block.
        """
        return [(row, col, code >= SETTLED_MIN) for row, col, code in self._find(BLOCK_MIN, SETTLED_MAX)]

    def pits(self):
        """
        Return every open pit as a list of ``(row, column)``.
        """
        return [(row, col) for row, col, _code in self._find(CODE_PIT, CODE_PIT)]

    def turnstiles(self):
        """
        Return every turnstile as a list of ``(row, column, arms)``.

        `arms` is a mask with bit 8 up, 4 right, 2 down and 1 left, read out of the
        cartridge's own shape table. Turning a turnstile rotates its arms and so changes the
        mask, which makes it state rather than scenery: which arms are where decides what a
        tater can walk through.
        """
        masks = self.shape_table()
        return [(row, col, masks[code - PIVOT_MIN] >> 4) for row, col, code in self._find(PIVOT_MIN, PIVOT_MAX)]

    def exit_cell(self):
        """
        Return where the room's exit flag is, as ``(row, column)``, or `None` when no room is
        loaded.
        """
        flags = self._find(EXIT_CODE, EXIT_CODE)
        return (flags[0][0], flags[0][1]) if flags else None

    def shape_table(self):
        """
        Return the fifteen turnstile shapes, straight out of the cartridge at 0x0BF6.
        """
        return self.pyboy.memory[ROM_BANK, SHAPE_TABLE_ADDR : SHAPE_TABLE_ADDR + SHAPE_TABLE_ENTRIES]

    def settle(self, max_ticks=SETTLE_MAX_TICKS, stable_ticks=SETTLE_STABLE_TICKS):
        """
        Run the emulator until the board stops changing, and report whether it did.

        The sprites are deliberately not part of this. On the other Game Boy puzzlers the
        piece in motion is a sprite and work RAM says nothing while it slides; here the
        opposite is true twice over. The board buffer is written for every part of a move, and
        the tater's idle bob rewrites the sprites every eight frames for as long as the game
        is running, so a rule that included them would never fire at all.

        Twenty frames of stillness is measured rather than guessed: nothing observed takes
        longer than sixteen frames of board writes, and the longest still spell *inside* an
        unfinished move is eight, when a block that has been shoved onto pits is dissolving
        into them.

        Once the last tater is home the cartridge starts its own sequence over the top of the
        room, so this returns the moment the room is solved: that is the last frame the solved
        board exists on.

        Args:
            max_ticks (int): Give up after this many frames
            stable_ticks (int): Frames the board must hold still

        Returns
        -------
        bool:
            Whether the board settled within `max_ticks`
        """
        previous = None
        stable = 0
        for _ in range(max_ticks):
            self.pyboy.tick(1, False, False)
            current = self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + BOARD_BYTES]
            if self.pyboy.memory[TATERS_ON_BOARD_ADDR] == 0:
                return True
            if current == previous:
                stable += 1
                if stable >= stable_ticks:
                    return True
            else:
                previous = current
                stable = 0
        return False

    def switch_tater(self, press_ticks=PRESS_TICKS):
        """
        Hand the controls to the next character, and wait out the lockout that follows.

        Select is the button, and pressing it changes nothing on the board, so the ordinary
        settle rule is satisfied the instant the press is made. The cartridge then ignores
        anything pressed inside the next 33 frames, which silently drops every second switch
        in a row: the plan and the game end up with different taters under the controls, and
        the boards only diverge several moves later.

        Args:
            press_ticks (int): Frames to hold select
        """
        self.pyboy.button(SWITCH_BUTTON, press_ticks)
        self.pyboy.tick(press_ticks + SWITCH_LOCKOUT_TICKS, False, False)
        self.settle()

    def _menu_cursor(self):
        """Which SELECT MODE entry is highlighted, or `None` when that menu is not up."""
        cursor = self.pyboy.memory[MENU_CURSOR_ADDR]
        return cursor if cursor < len(MODE_MENU_ROW) + 1 else None

    def _level_is_loaded(self):
        """`True` once a playable room sits in the board buffer.

        Four things have to agree, because none of them alone is enough: the dimension bytes
        keep whatever the last room left in them, the character mask is zero both before a
        room loads and after one is solved, and the buffer holds the previous room until the
        next one overwrites it.
        """
        if self.pyboy.memory[OVERLAY_ADDR] != 0:
            return False
        width, height = (self.pyboy.memory[BOARD_WIDTH_ADDR] - 2, self.pyboy.memory[BOARD_HEIGHT_ADDR] - 2)
        if not (MIN_ROOM <= width <= MAX_ROOM and MIN_ROOM <= height <= MAX_ROOM):
            return False
        if self.pyboy.memory[TATERS_ON_BOARD_ADDR] == 0:
            return False
        return bool(self._find(EXIT_CODE, EXIT_CODE))

    def _boot(self, mode):
        """Get from power-on to a loaded room in `mode`. `True` if one appeared.

        The front end is the title screen, then SELECT MODE, then, depending on the mode
        chosen, either a tutor with several screens of advice or an ENTER PASSWORD grid, and
        start advances all of them. Only one screen needs the d-pad: SELECT MODE, where
        BEGINNER MODE is already under the cursor and PUZZLE MODE is one press down.

        Knowing which screen is up is what the menu cursor byte is for. It holds 0x80 while
        the title is on screen and a small number everywhere a cursor exists, so the title
        screen is what marks the boundary: the first small number after it is SELECT MODE's
        highlight. That matters because PUZZLE MODE's password grid reuses the same byte as
        its own row cursor, and a d-pad press aimed at the mode menu but landing there walks
        the alphabet instead, which is why the boot stops touching the d-pad the moment the
        mode is chosen.
        """
        wanted = MODE_MENU_ROW[mode]
        past_title = False
        chosen = wanted == 0
        for _ in range(0, BOOT_MAX_TICKS, BOOT_STEP_TICKS):
            if self._level_is_loaded():
                return True
            cursor = self._menu_cursor()
            if not past_title:
                # 0x80 shows only while the title is up, so seeing it once and then seeing a
                # cursor is what says SELECT MODE has replaced it.
                past_title = cursor is None
                self.pyboy.button("start", BOOT_PRESS_TICKS)
            elif chosen or cursor is None:
                # Either the mode is picked, or the menu has not drawn itself yet. `chosen`
                # must not be set here: setting it on the frame between the title going away
                # and the menu appearing picks whatever the cursor happens to be resting on.
                self.pyboy.button("start", BOOT_PRESS_TICKS)
            elif cursor != wanted:
                self.pyboy.button("down", BOOT_PRESS_TICKS)
            else:
                chosen = True
                self.pyboy.button("start", BOOT_PRESS_TICKS)
            self.pyboy.tick(BOOT_STEP_TICKS, False, False)
        return self._level_is_loaded()

    def _wait_until_interactive(self):
        """Advance past the room's intro, and report how many frames it took.

        The loader fills the board buffer before the room has finished announcing itself, so
        the board is fully readable, and settled, while every button is still ignored, for
        about sixty frames. A game started in that window looks normal and answers nothing.

        Rather than hard-code the delay, this presses each button from a save state at
        increasing offsets until something answers, then rewinds and replays only the waiting,
        so the board handed back is still the one the loader built. Select counts as an
        answer, and has to: room A-14 opens with its first tater walled in on all four sides,
        and handing the controls to the other one is the only thing a player can do there.
        """
        start = io.BytesIO()
        self.pyboy.save_state(start)

        def rewind(waited):
            start.seek(0)
            self.pyboy.load_state(start)
            self.pyboy.tick(1, False, False)
            if waited:
                self.pyboy.tick(waited, False, False)

        def responds_after(waited):
            for button in DIRECTIONS + (SWITCH_BUTTON,):
                rewind(waited)
                before = (
                    self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + BOARD_BYTES],
                    self.pyboy.memory[ACTIVE_TATER_ADDR],
                )
                self.pyboy.button(button, PRESS_TICKS)
                self.pyboy.tick(PRESS_TICKS + 2, False, False)
                self.settle()
                after = (
                    self.pyboy.memory[BOARD_ADDR : BOARD_ADDR + BOARD_BYTES],
                    self.pyboy.memory[ACTIVE_TATER_ADDR],
                )
                if after != before:
                    return True
            return False

        waited = 0
        while waited <= INTRO_MAX_TICKS:
            if responds_after(waited):
                rewind(waited)
                return waited
            waited += INTRO_STEP_TICKS
        # Nothing answered. Either the room genuinely has no move in it, or the probe is
        # wrong; either way, wait out twice the delay that was measured and hand the room back
        # rather than fail on a room a bot could still legitimately be given.
        rewind(INTRO_FALLBACK_TICKS)
        return None

    def set_level(self, index):
        """
        Select the room the cartridge's loader will build, zero-based over set A and then set
        C: rooms 0-40 are PUZZLE MODE's and 41-104 are BEGINNER MODE's.

        This has to be called before `start_game`, because it also decides which entry of
        SELECT MODE the boot walks to. The loader is hooked rather than driven through the
        menus: it is entered with the level index in HL, and writing that is both exact and
        the only write, so the cartridge stays in a state it put itself in.

        Args:
            index (int): The room to load, or `None` to take whichever room the mode opens with
        """
        if index is not None:
            _within_set(index)
        self._forced_level[0] = None if index is None else _within_set(index)[1]
        self.level = 0 if index is None else index
        if index is not None and not self._hook_registered:
            self.pyboy.hook_register(ROM_BANK, LOAD_LEVEL, _force_level, (self.pyboy, self._forced_level))
            self._hook_registered = True

    def level_label(self, index=None):
        """
        Return how the cartridge's own menus number a room, as ``"set-number"`` counting from
        one: `level_label(0)` is ``"A-01"``.

        Args:
            index (int): The room to name. Defaults to the one `set_level` selected
        """
        letter, within, _mode = _within_set(self.level if index is None else index)
        return f"{letter}-{within + 1:02d}"

    def start_game(self, timer_div=None, level=None):
        """
        Call this function right after initializing PyBoy. This navigates the title screen and
        SELECT MODE, and gives back control on the first frame the room answers a button.

        The state of the emulator is saved, and using `reset_game`, you can get back to this
        point of the game instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            * level (int): Room to load, zero-based over set A and then set C
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset_game' instead.")

        if level is not None:
            self.set_level(level)

        mode = _within_set(self.level)[2]
        if not self._boot(mode):
            raise PyBoyException(f"No room was loaded within {BOOT_MAX_TICKS} frames of booting")

        self.settle()
        self._wait_until_interactive()
        self.taters_total = bin(self.pyboy.memory[TATERS_ON_BOARD_ADDR]).count("1")

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to put the room back
        the way the loader built it.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self.taters_total = bin(self.pyboy.memory[TATERS_ON_BOARD_ADDR]).count("1")

    def level_solved(self):
        """
        Return whether every character has reached the exit flag, which is how a room is won.

        This is the cartridge's own answer, read from the character mask rather than from the
        board. The board cannot answer it: a tater in mid-step is taken off the board and drawn
        as a sprite until it arrives, so for a dozen frames after every press the board shows
        no tater at all, which is indistinguishable from a solved room.
        """
        return self.taters_total > 0 and self.pyboy.memory[TATERS_ON_BOARD_ADDR] == 0

    def game_over(self):
        """
        Always `False`. A room in PUZZLE or BEGINNER mode cannot be lost: there is no clock,
        and nothing on the board can kill a tater.

        A room can still be made unsolvable -- a block settled into the one pit that had to be
        crossed somewhere else is gone for good, and so is the room -- but the cartridge does
        not flag that, and recognising it needs reachability under moving turnstiles rather
        than a byte in RAM. Restart the room with `reset_game` when a bot gets stuck.
        """
        return False

    def __repr__(self):
        board = self._game_area_tiles().tolist()
        lines = []
        for row in range(BOARD_ROWS):
            line = "".join([CELL_GLYPHS.get(board[row][col], "?") for col in range(BOARD_COLS)])
            if line.strip():
                lines.append(line.rstrip())
        return (
            "Amazing Tater:\n"
            + f"Room: {self.level_label()} (index {self.level})\n"
            + f"Size: {self.room_size[0]}x{self.room_size[1]}\n"
            + f"Taters home: {self.taters_home}/{self.taters_total}\n"
            + f"Controls on tater: {self.active_tater + 1}\n"
            + "Board:\n"
            + "\n".join(lines)
        )
