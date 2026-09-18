#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperFlipull.cartridge_title": False,
    "GameWrapperFlipull.post_tick": False,
}

import io

import numpy as np

import pyboy
from pyboy.api.constants import TILES
from pyboy.utils import PyBoyException, PyBoyInvalidInputException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# The block field. 14 rows of 32 bytes, of which only the first 16 columns carry meaning.
FIELD_ADDR = 0xC840
ROW_STRIDE = 0x20
FIELD_ROWS = 14
FIELD_COLS = 16
FIELD_BYTES = FIELD_ROWS * ROW_STRIDE

CELL_OUTSIDE = 0x00  # Outside the field
CELL_BORDER = 0x80  # Ceiling, floor and the left wall
BLOCK_MIN = 0x83  # 0x83-0x86 are the four playable block types
BLOCK_MAX = 0x86
CELL_STAIRCASE = 0x87  # Fixed structural diagonal. Never clearable

FLOOR_ROW = FIELD_ROWS - 1

CELL_GLYPHS = {CELL_OUTSIDE: " ", CELL_BORDER: "#", CELL_STAIRCASE: "="}

# Flipull keeps its counters as separate decimal digits, ones first: not binary, and not
# packed BCD. Searching for 25 or 0x19 finds nothing; the value is 05 and 02 in adjacent
# bytes. Nearly every counter is in HRAM rather than in work RAM.
BLOCKS_ONES_ADDR = 0xFFC9
BLOCKS_TENS_ADDR = 0xFFCA
INITIAL_ONES_ADDR = 0xFFC0  # The stage's starting total, not the live one
INITIAL_TENS_ADDR = 0xFFC1
TIMER_SECONDS_ONES_ADDR = 0xFFCB
TIMER_SECONDS_TENS_ADDR = 0xFFCC
TIMER_MINUTES_ADDR = 0xFFCE
CLEAR_TARGET_ADDR = 0xFFCF  # The CLEAR number: how few blocks finish the stage

# The stage number is kept as two decimal digits, and both are read straight into the HUD.
STAGE_ONES_ADDR = 0xFFC6
STAGE_TENS_ADDR = 0xFFC7

# 0:2D55 is the loader. It reads both stage digits, indexes a table of pointers at 0x3A0E,
# and copies the three bytes each one points at into the HUD counters.
STAGE_LOADER_ADDR = 0x2D55
STAGE_TABLE_ADDR = 0x3A0E
STAGE_COUNT = 32
STAGE_DESCRIPTOR_BYTES = 3  # Clear target, blocks ones, blocks tens
ROM_BANK = 0  # No mapper: the whole ROM is flat at 0x0000-0x7FFF

# A thrown block is a sprite until it lands, so the field sits still for the thirty-odd
# frames it spends crossing the screen. Both are watched by `settle`.
LAST_THROWN_ADDR = 0xFFD4  # The block previously in hand, i.e. the one just thrown
THROW_COUNT_ADDRS = (0xFFD2, 0xFFD3)  # A count of completed throws, not an in-flight flag
OAM_BUFFER_ADDR = 0xC000
OAM_BUFFER_BYTES = 160

SETTLE_MAX_TICKS = 900  # The longest throw measured took 169 frames
SETTLE_STABLE_TICKS = 10
BOOT_MAX_TICKS = 2400
BOOT_PRESS_EVERY = 12

# How the cartridge wants to be driven. `calibrate` measures all of this off the ROM in
# hand; the values here are only what it falls back to when a probe comes up empty.
PRESS_TICKS = 5  # Flipull's d-pad repeats on frame 11, so the window is (1, 10)
PROBE_MAX_HOLD = 60
THROW_BUTTONS = ("a", "b")  # Which one throws is probed, not assumed
MOVE_BUTTONS = ("up", "down")

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
mapping_compressed[CELL_BORDER] = 1
mapping_compressed[CELL_STAIRCASE] = 2
for _type, _cell in enumerate(range(BLOCK_MIN, BLOCK_MAX + 1)):
    mapping_compressed[_cell] = 3 + _type
"""
Compressed mapping for `pyboy.PyBoy.game_area_mapping`
"""

mapping_minimal = np.zeros(TILES, dtype=np.uint8)
mapping_minimal[CELL_BORDER] = 1
mapping_minimal[CELL_STAIRCASE] = 1
mapping_minimal[BLOCK_MIN : BLOCK_MAX + 1] = 2
"""
Minimal mapping for `pyboy.PyBoy.game_area_mapping`
"""


def _decode_digits(tens, ones):
    """Flipull stores counters as separate decimal digits, ones first."""
    return tens * 10 + ones


def _stage_digits(stage):
    """The two bytes the cartridge keeps a stage number in. `stage` is 1-based.

    0:1673 is the advance: `inc ($FFC6)`, and at ten it zeroes that and carries into 0xFFC7.
    So the pair is a two-digit decimal number, tens then ones, and the loader's table index
    is `10*tens + ones - 1`.
    """
    return stage // 10, stage % 10


def _force_stage(context):
    """Hook body: write the stage digits each time the loader is reached.

    This is not the same as poking a layout in behind the game's back. The two bytes written
    are the game's own stage number, they are written before anything reads them, and every
    place that reads them afterwards -- the field builder and the HUD among them -- agrees:
    the on-screen STAGE number really is the one asked for.
    """
    pyboy_instance, stage = context
    if stage[0] is not None:
        tens, ones = _stage_digits(stage[0])
        pyboy_instance.memory[STAGE_TENS_ADDR] = tens
        pyboy_instance.memory[STAGE_ONES_ADDR] = ones


class GameWrapperFlipull(PyBoyGameWrapper):
    """
    This class wraps Flipull, and provides easy access to the block field, the counters and
    the stage table for AIs.

    Flipull sits the player at the right of a wall of blocks holding one of them, free to
    move up and down the rows or to throw. A throw sends the block left, blocks of its own
    type are destroyed, a destroyed block drops its column, and something comes back into his
    hand. The stage is finished when few enough blocks are left: the HUD's CLEAR number, not
    zero.

    The field lives in work RAM rather than in the tilemap, so `game_area` is read from
    there. The values are the cartridge's own cell types.

    If you call `print` on an instance of this object, it will show an overview of everything
    this object provides.
    """

    cartridge_title = "FLIPULL"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`

    Empty cells are `0`, the border is `1`, the staircase is `2`, and the four block types
    are `3` to `6`.
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`

    Empty cells are `0`, anything structural is `1`, and every block is `2`.
    """

    def __init__(self, *args, **kwargs):
        self.stage = 0
        """The stage number shown on the HUD, 1-based"""
        self.blocks_remaining = 0
        """The number of blocks left on the field"""
        self.blocks_initial = 0
        """The number of blocks the stage started with"""
        self.blocks_cleared = 0
        """The number of blocks destroyed so far. Can be used for AI scoring"""
        self.clear_target = 0
        """How few blocks have to be left for the stage to be finished"""
        self.time_left = 0
        """The number of seconds left on the clock"""
        self.throws = 0
        """The number of throws that have connected. A throw that changes nothing doesn't count"""
        self.press_ticks = PRESS_TICKS
        """How many frames to hold a direction to move exactly one row. Measured by `GameWrapperFlipull.calibrate`"""
        self.throw_button = THROW_BUTTONS[0]
        """Which button throws the block in hand. Measured by `GameWrapperFlipull.calibrate`"""
        self.player_sprite = None
        """Which OAM slot the player is drawn in, or `None`. Measured by `GameWrapperFlipull.calibrate`"""
        self.held_sprite = None
        """Which OAM slot the block in his hand is drawn in, or `None`. Measured by `GameWrapperFlipull.calibrate`"""
        self.row_pitch = 0
        """How many pixels apart two rows are drawn, or `0`. Measured by `GameWrapperFlipull.calibrate`"""
        self.row_span = None
        """The highest and lowest sprite Y the player can stand on, or `None`. Measured by `GameWrapperFlipull.calibrate`"""

        self._forced_stage = [None]
        self._hook_registered = False

        super().__init__(*args, game_area_section=(0, 0, FIELD_COLS, FIELD_ROWS), game_area_follow_scxy=False, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.stage = _decode_digits(self.pyboy.memory[STAGE_TENS_ADDR], self.pyboy.memory[STAGE_ONES_ADDR])
        self.blocks_remaining = _decode_digits(self.pyboy.memory[BLOCKS_TENS_ADDR], self.pyboy.memory[BLOCKS_ONES_ADDR])
        self.blocks_initial = _decode_digits(self.pyboy.memory[INITIAL_TENS_ADDR], self.pyboy.memory[INITIAL_ONES_ADDR])
        self.blocks_cleared = self.blocks_initial - self.blocks_remaining
        self.clear_target = self.pyboy.memory[CLEAR_TARGET_ADDR]
        self.time_left = (
            self.pyboy.memory[TIMER_MINUTES_ADDR] * 60
            + self.pyboy.memory[TIMER_SECONDS_TENS_ADDR] * 10
            + self.pyboy.memory[TIMER_SECONDS_ONES_ADDR]
        )
        # A count of completed throws rather than a flag: it stays put for a throw that
        # changes nothing, and it stays 0 for the whole flight, rising only when the block
        # lands.
        self.throws = max(self.pyboy.memory[THROW_COUNT_ADDRS[0]], self.pyboy.memory[THROW_COUNT_ADDRS[1]])

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            raw = self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES]
            self._cached_game_area_tiles = np.asarray(
                [[raw[ROW_STRIDE * row + col] for col in range(FIELD_COLS)] for row in range(FIELD_ROWS)],
                dtype=np.uint32,
            )
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the 14 by 16 block field as a matrix of the cartridge's cell types.

        The player and the block in his hand are sprites and are not part of the field. Use
        `GameWrapperFlipull.player_row` and `GameWrapperFlipull.held_block` for those.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the block field
        """
        return self.mapping[self._game_area_tiles()]

    def blocks(self):
        """
        Return every playable block on the field as a list of ``(row, column, type)``.

        The staircase and the border are structural and are never in the list: they cannot be
        destroyed, whatever is thrown at them.
        """
        raw = self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES]
        blocks = []
        for row in range(FIELD_ROWS):
            for col in range(FIELD_COLS):
                value = raw[ROW_STRIDE * row + col]
                if BLOCK_MIN <= value <= BLOCK_MAX:
                    blocks.append((row, col, value - BLOCK_MIN + 1))
        return blocks

    def row_blocks(self, row):
        """
        Return one row of the field left to right, as ``(column, type)`` for the blocks in it.

        This is offered for an AI reasoning about a row, not as a model of what a throw does.
        Driven across all twelve reachable rows of stage 1, every row connects -- empty ones
        included -- so a thrown block plainly travels further than its own row, and what
        decides where it lands is deliberately not modelled here.

        Args:
            row (int): The field row, counting down from the ceiling
        """
        if row is None or not 0 <= row < FIELD_ROWS:
            return []
        raw = self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES]
        return [
            (col, raw[ROW_STRIDE * row + col] - BLOCK_MIN + 1)
            for col in range(FIELD_COLS)
            if BLOCK_MIN <= raw[ROW_STRIDE * row + col] <= BLOCK_MAX
        ]

    def _shadow_oam(self):
        """The OAM DMA buffer as ``(y, x, tile)`` for all forty sprite slots, parked ones included.

        Read from the buffer rather than through `pyboy.PyBoy.get_sprite`, because the slots
        have to keep their indices from frame to frame: which slot is the player and which is
        the block in his hand is worked out by watching them move.
        """
        buffer = self.pyboy.memory[OAM_BUFFER_ADDR : OAM_BUFFER_ADDR + OAM_BUFFER_BYTES]
        return [(buffer[i], buffer[i + 1], buffer[i + 2]) for i in range(0, OAM_BUFFER_BYTES, 4)]

    def stages(self):
        """
        Return the stage list, read out of the cartridge rather than transcribed.

        0x3A0E is a table of little-endian pointers, each pointing at three bytes: the CLEAR
        target, then the block total as ones and tens digits, in the same digit-per-byte
        spelling the HUD counters use. The loader indexes it with `10*tens + ones - 1`.

        Returns a list of ``(stage, clear_target, blocks)`` tuples, 1-based on the stage
        number. The table is followed in ROM by a shorter second one, so the parse stops when
        an entry stops looking like a stage rather than trusting the count.
        """
        stages = []
        for index in range(STAGE_COUNT):
            pointer = STAGE_TABLE_ADDR + 2 * index
            low, high = self.pyboy.memory[ROM_BANK, pointer : pointer + 2]
            target = low | (high << 8)
            if target + STAGE_DESCRIPTOR_BYTES > 0x8000:
                break
            clear, ones, tens = self.pyboy.memory[ROM_BANK, target : target + STAGE_DESCRIPTOR_BYTES]
            if ones > 9 or tens > 9 or clear > 99 or not (tens * 10 + ones):
                break
            stages.append((index + 1, clear, tens * 10 + ones))
        return stages

    def settle(self, max_ticks=SETTLE_MAX_TICKS, stable_ticks=SETTLE_STABLE_TICKS):
        """
        Run the emulator until the game stops moving, and report whether it did.

        Settled means the field **and the sprites** identical for `stable_ticks` frames. The
        sprites are the half that is easy to miss: a thrown block is a sprite until it lands,
        so the field sits still for the thirty-odd frames it spends crossing the screen, and
        waiting on the field alone reads a position mid-throw. Watching the sprites covers the
        whole cycle: the flight out, the landing that changes the field and drops a column,
        and the arc back to the player's hand.

        Args:
            max_ticks (int): Give up after this many frames
            stable_ticks (int): Frames the field and the sprites must hold still

        Returns
        -------
        bool:
            Whether the game settled within `max_ticks`
        """
        previous = None
        stable = 0
        for _ in range(max_ticks):
            self.pyboy.tick(1, False, False)
            now = (self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES], self._shadow_oam())
            if now == previous:
                stable += 1
                if stable >= stable_ticks:
                    return True
            else:
                previous = now
                stable = 0
        return False

    def set_stage(self, stage):
        """
        Select the stage the cartridge's loader will build, 1-based: `set_stage(8)` is stage 8.

        This has to be called before `start_game`. The loader is hooked, and the stage's two
        decimal digits are written as it arrives, because a title screen sets them and calls
        the loader within the same frame.

        Args:
            stage (int): The stage to load, or `None` to leave the cartridge alone
        """
        if stage is not None and not 1 <= stage <= STAGE_COUNT:
            raise PyBoyInvalidInputException(
                f"{stage} is out of bounds. This cartridge has {STAGE_COUNT} stages, so only values between 1 and "
                f"{STAGE_COUNT} are allowed. Past the end of the table the loader reads whatever follows it in ROM "
                "and silently builds some other stage."
            )
        self._forced_stage[0] = stage
        if stage is not None and not self._hook_registered:
            self.pyboy.hook_register(ROM_BANK, STAGE_LOADER_ADDR, _force_stage, (self.pyboy, self._forced_stage))
            self._hook_registered = True

    def start_game(self, timer_div=None, stage=None, seed_ticks=0):
        """
        Call this function right after initializing PyBoy. This taps through the title screens
        and gives back control on the first frame a stage is on the field.

        The state of the emulator is saved, and using `reset_game`, you can get back to this
        point of the game instantly.

        The cartridge's stage table fixes only the block total and the CLEAR target: the
        block *arrangement* is drawn from a generator that runs while the console boots. A
        boot that always takes the same number of frames therefore always builds the same
        board, which is what makes `reset_game` repeatable, and `seed_ticks` is how to ask for
        a different one: the frames are spent idling before the title screen is touched, and
        the same number always gives the same board. Seven frames per stage was enough to give
        all 32 stages a board of their own.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            * stage (int): Stage to force on the loader, 1-based
            * seed_ticks (int): Frames to idle before booting, which redraws the block arrangement
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset_game' instead.")

        if stage is not None:
            self.set_stage(stage)

        if seed_ticks:
            self.pyboy.tick(seed_ticks, False, False)

        for frame in range(0, BOOT_MAX_TICKS, BOOT_PRESS_EVERY):
            self.pyboy.button("start" if (frame // BOOT_PRESS_EVERY) % 2 == 0 else "a", 4)
            self.pyboy.tick(BOOT_PRESS_EVERY, False, False)
            if self._stage_is_loaded():
                break
        else:
            raise PyBoyException(f"No stage was loaded within {BOOT_MAX_TICKS} frames of booting")

        # Stop forcing now that the stage is up, so the cartridge behaves normally from here:
        # a cleared stage advances to the next one, and a lost life reloads this one.
        self._forced_stage[0] = None
        self._check_stage(stage)
        self.settle()

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game back
        to the first frame of the stage `start_game` reached, block arrangement included.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

    def _stage_is_loaded(self):
        """`True` once a field with blocks on it is up and agrees with the HUD counter."""
        remaining = _decode_digits(self.pyboy.memory[BLOCKS_TENS_ADDR], self.pyboy.memory[BLOCKS_ONES_ADDR])
        if remaining == 0:
            return False
        # The field and the HUD counter have to agree: 25 cells holding a block against
        # BLOCK 25 on screen.
        return len(self.blocks()) == remaining

    def _check_stage(self, stage):
        """Whether the stage that loaded is the one the ROM's own table said it would be.

        The table gives a block total and a CLEAR target per stage, and no two neighbours
        share both, so this catches a selection that silently did not take. That is the
        failure worth catching, because a wrong stage still looks like a good one.
        """
        if stage is None:
            return
        stages = {number: (clear, blocks) for number, clear, blocks in self.stages()}
        if stage not in stages:
            return
        clear, blocks = stages[stage]
        got = (self.stage, self.clear_target, self.blocks_remaining)
        if got != (stage, clear, blocks):
            raise PyBoyException(
                f"Selecting stage {stage} did not take: the cartridge came up on stage {got[0]} with {got[2]} blocks "
                f"and a target of {got[1]}, where the ROM's own table says stage {stage} has {blocks} blocks and a "
                f"target of {clear}."
            )

    def calibrate(self, max_hold=PROBE_MAX_HOLD):
        """
        Measure how this cartridge wants to be driven, and remember the answers.

        Four things are needed to drive Flipull and none of them is in RAM: which button
        throws, which OAM slots the player and the block in his hand are drawn in, how long a
        direction has to be held to move exactly one row, and how far apart the rows are
        drawn. They are all properties of the cartridge rather than of the stage, so one call
        per ROM is enough.

        Every probe rewinds to the state the call started from, so nothing it does survives;
        it costs a couple of hundred frames of emulation. The results land in
        `GameWrapperFlipull.throw_button`, `GameWrapperFlipull.press_ticks`,
        `GameWrapperFlipull.player_sprite`, `GameWrapperFlipull.held_sprite`,
        `GameWrapperFlipull.row_pitch` and `GameWrapperFlipull.row_span`.

        Args:
            max_hold (int): The longest hold to try before giving up on the repeat rate
        """
        snapshot = io.BytesIO()
        self.pyboy.save_state(snapshot)

        # The throw button first: it needs nothing else, and telling the player apart from the
        # block in his hand needs a throw to separate them.
        self.throw_button = self._probe_throw_button(snapshot) or THROW_BUTTONS[0]
        player, held, move_button = self._probe_sprites(snapshot)
        self.player_sprite = player
        self.held_sprite = held
        window, pitch = self._measure_hold_window(snapshot, player, move_button, max_hold)
        self.row_pitch = pitch or 0
        self.press_ticks = (window[0] + window[1]) // 2 if window else PRESS_TICKS
        self.row_span = self._measure_row_span(snapshot, player)

        self._rewind(snapshot)

    def _rewind(self, snapshot):
        snapshot.seek(0)
        self.pyboy.load_state(snapshot)
        self.pyboy.tick(1, False, False)

    def _tap(self, button, hold, gap=2):
        self.pyboy.button(button, hold)
        self.pyboy.tick(hold + gap, False, False)

    def _probe_throw_button(self, snapshot):
        """Which button throws, found by pressing each and watching for a throw.

        A throw shows up in two independent places -- the completed-throw count goes up, and
        the field changes -- so a button that only moves the player is not mistaken for one.
        Both are checked after settling, because neither happens until the block lands, some
        thirty frames after the press. On Flipull both A and B throw; the first that does is
        the one taken.
        """
        for button in THROW_BUTTONS:
            self._rewind(snapshot)
            before = self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES]
            throws_before = self.throws
            self._tap(button, PRESS_TICKS)
            self.settle()
            if self.throws != throws_before or self.pyboy.memory[FIELD_ADDR : FIELD_ADDR + FIELD_BYTES] != before:
                self._rewind(snapshot)
                return button
        self._rewind(snapshot)
        return None

    def _probe_sprites(self, snapshot):
        """Which OAM slots are the player and the block in his hand, and which way he can move.

        Two things the cartridge taught this probe. The player may start against a wall --
        Flipull opens with him on the bottom row, where `down` moves nothing -- so a blocked
        direction is allowed, and what is required instead is that no candidate ever move the
        *wrong* way. And more than one sprite moves, because the player and the block travel
        together, so they are told apart by throwing: the held block flies off across the
        field, the player does not move.

        Returns ``(player, held, move_button)``, any of which may be `None`.
        """
        self._rewind(snapshot)
        before = self._shadow_oam()
        deltas = {}
        moved_by = {}
        for button in MOVE_BUTTONS:
            self._rewind(snapshot)
            self._tap(button, PRESS_TICKS)
            self.settle()
            after = self._shadow_oam()
            deltas[button] = [now[0] - was[0] for was, now in zip(before, after)]
            moved_by[button] = after != before
        self._rewind(snapshot)

        up, down = deltas[MOVE_BUTTONS[0]], deltas[MOVE_BUTTONS[1]]
        candidates = [i for i in range(len(before)) if before[i][0] and up[i] <= 0 <= down[i] and (up[i] or down[i])]
        if not candidates:
            return None, None, None

        # Whichever direction actually got the player off the row he starts on is the one the
        # hold window can be measured with; the other may be into a wall.
        move_button = next((button for button in MOVE_BUTTONS if moved_by[button]), MOVE_BUTTONS[0])
        if len(candidates) == 1:
            return candidates[0], None, move_button

        self._rewind(snapshot)
        self._tap(self.throw_button, PRESS_TICKS)
        self.pyboy.tick(20, False, False)
        midflight = self._shadow_oam()
        self._rewind(snapshot)
        stayed = [i for i in candidates if midflight[i] == before[i]]
        left = [i for i in candidates if midflight[i] != before[i]]
        if len(stayed) == 1:
            return stayed[0], (left[0] if len(left) == 1 else None), move_button
        return None, None, move_button

    def _measure_hold_window(self, snapshot, sprite, button, max_hold):
        """The closed range of holds that move the player exactly one row, and the row pitch.

        Too short and the press is never sampled; too long and auto-repeat moves two rows, so
        the position is not the one the press asked for. `button` is the direction the player
        can actually move in, because on Flipull he starts on the bottom row and probing
        `down` into the floor concludes that he never moves.
        """
        if sprite is None:
            return None, None
        step = None
        low = None
        for hold in range(1, max_hold + 1):
            self._rewind(snapshot)
            origin = self._shadow_oam()[sprite][0]
            self._tap(button or MOVE_BUTTONS[0], hold)
            self.settle()
            moved = abs(self._shadow_oam()[sprite][0] - origin)
            if moved == 0:
                continue
            if step is None:
                step, low = moved, hold
            elif moved >= 2 * step:
                self._rewind(snapshot)
                return (low, hold - 1), step
        self._rewind(snapshot)
        return (None if low is None else (low, max_hold)), step

    def _measure_row_span(self, snapshot, sprite, max_rows=FIELD_ROWS + 2):
        """The highest and lowest sprite Y the player can stand on, walked out on the cartridge.

        This is what turns his sprite Y into a field row: the bottom of the walk is the row
        just above the floor. Twelve rows on Flipull, which is the field's 14 minus the
        ceiling and the floor.
        """
        if sprite is None:
            return None
        span = []
        for button in MOVE_BUTTONS:
            self._rewind(snapshot)
            y = self._shadow_oam()[sprite][0]
            for _ in range(max_rows):
                self._tap(button, self.press_ticks)
                self.settle()
                moved = self._shadow_oam()[sprite][0]
                if moved == y:
                    break
                y = moved
            span.append(y)
        self._rewind(snapshot)
        return min(span), max(span)

    def player_row(self):
        """
        Return the field row the player is standing on, or `None` when it isn't known.

        The player has no row variable anywhere in RAM: the only thing that says where he is,
        is his sprite. Which sprite that is, and how far apart the rows are drawn, come from
        `GameWrapperFlipull.calibrate`, so this returns `None` until that has been called.

        The row is anchored at the bottom rather than the top: the lowest row he can reach is
        the one just above the floor, and every row above it is a row pitch further up.
        """
        if self.player_sprite is None or not self.row_pitch or self.row_span is None:
            return None
        y = self._shadow_oam()[self.player_sprite][0]
        return (FLOOR_ROW - 1) - (self.row_span[1] - y) // self.row_pitch

    def held_block(self):
        """
        Return the type of the block in the player's hand, or `None` when it can't be read.

        0xFFD4 looks like this and is not: driven across five throws it holds the block
        *previously* in hand -- the one just thrown -- lagging the hand by one throw and
        reading 0x00 until the first throw of a stage. The hand sprite's tile is the live
        value, and it uses the same encoding the field does, which is why this needs
        `GameWrapperFlipull.calibrate` to have found the sprite first.

        At stage start the tile reads 0x82, which is not a block value at all, so this returns
        `None` rather than inventing one. Throwing once and reading
        `GameWrapperFlipull.last_thrown` names the block that was in hand.
        """
        if self.held_sprite is None:
            return None
        tile = self._shadow_oam()[self.held_sprite][2]
        return tile - BLOCK_MIN + 1 if BLOCK_MIN <= tile <= BLOCK_MAX else None

    def last_thrown(self):
        """
        Return the type of the block that was thrown last, or `None` before the first throw.
        """
        thrown = self.pyboy.memory[LAST_THROWN_ADDR]
        return thrown - BLOCK_MIN + 1 if BLOCK_MIN <= thrown <= BLOCK_MAX else None

    def stage_cleared(self):
        """
        Return whether few enough blocks are left for the stage to be finished.

        Flipull ends a stage when the count is down to the CLEAR number rather than to zero:
        the HUD shows BLOCK 25 against CLEAR 09.
        """
        return self.blocks_initial > 0 and self.blocks_remaining <= self.clear_target

    def game_over(self):
        """
        Return whether the clock has run out, which is how a life is lost in Flipull.
        """
        return self.blocks_initial > 0 and self.time_left == 0

    def __repr__(self):
        field = self._game_area_tiles().tolist()
        lines = []
        for row in range(FIELD_ROWS):
            line = []
            for col in range(FIELD_COLS):
                value = int(field[row][col])
                if BLOCK_MIN <= value <= BLOCK_MAX:
                    line.append(str(value - BLOCK_MIN + 1))
                else:
                    line.append(CELL_GLYPHS.get(value, "?"))
            lines.append("".join(line))
        return (
            "Flipull:\n"
            + f"Stage: {self.stage}\n"
            + f"Blocks: {self.blocks_remaining}/{self.blocks_initial}\n"
            + f"Clear target: {self.clear_target}\n"
            + f"Time left: {self.time_left}\n"
            + f"Held block: {self.held_block()}\n"
            + "Field:\n"
            + "\n".join(lines)
        )
