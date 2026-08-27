#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

import pyboy
from pyboy.api.constants import TILES_CGB
from pyboy.utils import PyBoyException, PyBoyInvalidInputException, bcd_to_dec

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

ADDR_LEVEL_SET = 0xC160
ADDR_SUBLEVEL = 0xC162
ADDR_LEVEL = 0xC163
ADDR_SCORE = 0xC17A
ADDR_TIME_LEFT = 0xC17D
ADDR_LIVES_LEFT = 0xC17F
ADDR_COINS = 0xC1F2
ADDR_MENU_SELECTION = 0xC1A8
ADDR_CHALLENGE_UNLOCK = 0xC18E
ADDR_PLAYER_STATE = 0xC1C1
ADDR_PLAYER_X = 0xC1CA
ADDR_PLAYER_Y = 0xFFA9
ADDR_LEVEL_X = 0xFFA7
ADDR_CAMERA_X_LOW = 0xFFB8
ADDR_CAMERA_X_HIGH = 0xFFB9
ADDR_CAMERA_Y = 0xFFBA
ADDR_MODE = 0xFFB5

MODE_TITLE_SCREEN = 0x03
MODE_MAIN_MENU = 0x19
MODE_FILE_SELECT = 0x17
MODE_OVERWORLD_INIT = 0x04
MODE_WORLD_MAP = 0x05
MODE_LEVEL = 0x0B
MODE_DEBUG_INIT = 0x31
MODE_DEBUG_MENU = 0x32
MODE_CHALLENGE_SELECT = 0x1E
STUCK_TIMEOUT_FRAMES = 600
MAX_PROGRESS_DELTA_PER_FRAME = 32

# The table is in ROM bank 3 at 03:6D16 (Tile16_InteractTypes).
INTERACTION_TABLE_BANK = 3
INTERACTION_TABLE_ADDRESS = 0x6D16
METATILE_MAP_BANK = 6
METATILE_MAP_ADDRESS = 0xD000
METATILE_MAP_WIDTH = 256
METATILE_MAP_HEIGHT = 16
METATILE_SCREEN_WIDTH = 16
METATILE_SCREEN_SIZE = 0x100
DEFAULT_SPRITE_OFFSET = 0

mapping_minimal = np.arange(TILES_CGB, dtype=np.uint32)
mapping_minimal[
    [2, 3, 4, 5, *range(68, 74), *range(84, 92), *range(96, 100), 138, 139, *range(176, 184), *range(186, 190)]
] = 0
# TODO: Mapping depends on level type. We could make a lookup table of levels to
# mappings (should be many reused mappings) or hash the tile data to find table.
# Otherwise we could hash every tile data independently and make a lookup table to ID it. In case they move. This is scanned at the beginning of each world-level.
#
#
# The following is only a mapping for 1-1 until validated elsewhere
mapping_minimal[[128, 129, 130, 131, 136, 137]] = 8  # Brick
mapping_minimal[[132, 133, *range(168, 172)]] = 0  # Castle
mapping_minimal[[*range(28, 34), *range(92, 96)]] = 12  # Fireball
mapping_minimal[[48, 49, *range(80, 84)]] = 15  # Flag
mapping_minimal[[46, 47, *range(114, 118)]] = 11  # Flower
mapping_minimal[[52, 53, 54, 55]] = 7  # Goomba
mapping_minimal[[*range(0, 8), *range(16, 24)]] = 1  # Mario
mapping_minimal[[42, 43, 44, 45]] = 9  # Mushroom #Also platforms with bowser ???
mapping_minimal[[100, 101]] = 14  # Star
mapping_minimal[[*range(56, 68)]] = 13  # Turtle
mapping_compressed = mapping_minimal

CUSTOM_LEVEL_SEQUENCE = (
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 1),
    (2, 3),
    (3, 1),
    (3, 2),
    (3, 3),
    (4, 1),
    (4, 2),
    (4, 3),
    (5, 1),
    (5, 2),
    (5, 3),
)


background_mapping_minimal = np.full(0x17, 3, dtype=np.uint32)
background_mapping_minimal[0] = 0
background_mapping_minimal[2] = 2
background_mapping_minimal[[5, 9, 10]] = 4
background_mapping_minimal[[4, 11, 19]] = 5
background_mapping_minimal[[6, 20, 22]] = 6


class GameWrapperSuperMarioBrosDeluxe(PyBoyGameWrapper):
    """
    Wrapper for Super Mario Bros. Deluxe.

    The optional ``level`` argument to :meth:`start_game` uses the game's
    unused level selector for normal gameplay. For the original game, levels
    0 through 31 are World 1-1 through World 8-4. Set
    ``super_player_levels=True`` for the For Super Players levels.
    """

    cartridge_title = "MARIO DELUXAHY"
    mapping_minimal = mapping_minimal
    mapping_compressed = mapping_compressed

    def __init__(self, *args, **kwargs):
        self.world = (0, 0)
        self.level = 0
        self.selected_level = 0
        self.selected_super_player_levels = False
        self.level_selected = False
        self.coins = 0
        self.lives_left = 0
        self.score = 0
        self.time_left = 0
        self.level_progress = 0
        self.stuck = False
        self.stuck_frames = 0
        self._stuck_last_progress = 0
        self._stuck_in_level = False
        self.custom_level_sequence_index = -1
        self.custom_next_level_prepared = False
        super().__init__(*args, game_area_section=(0, 6, 20, 26), game_area_follow_scxy=False, **kwargs)
        self.metatile_interaction_types = None
        self.mapping = mapping_minimal

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        if self.pyboy.memory[ADDR_MODE] == MODE_OVERWORLD_INIT and not self.custom_next_level_prepared:
            if 0 <= self.custom_level_sequence_index < len(CUSTOM_LEVEL_SEQUENCE) - 1:
                next_world, next_level = CUSTOM_LEVEL_SEQUENCE[self.custom_level_sequence_index + 1]
                next_level_id = (next_world - 1) * 4 + next_level - 1
                self.pyboy.memory[ADDR_LEVEL_SET] = 0
                self.pyboy.memory[ADDR_SUBLEVEL] = next_level_id
                self.pyboy.memory[ADDR_LEVEL] = next_level_id
                self.custom_level_sequence_index += 1
                self.custom_next_level_prepared = True

        self.level = self.pyboy.memory[ADDR_LEVEL]
        self.world = (int(self.level // 4 + 1), int(self.level % 4 + 1)) if self.level < 0x20 else (0, int(self.level))
        self.coins = self.pyboy.memory[ADDR_COINS]
        self.lives_left = self.pyboy.memory[ADDR_LIVES_LEFT]
        self.score = bcd_to_dec(int.from_bytes(self.pyboy.memory[ADDR_SCORE : ADDR_SCORE + 3], "little"), byte_width=3)
        # Deluxe stores the countdown as a little-endian binary integer.
        self.time_left = int.from_bytes(self.pyboy.memory[ADDR_TIME_LEFT : ADDR_TIME_LEFT + 2], "little")
        self.level_progress = self.pyboy.memory[ADDR_LEVEL_X] + int.from_bytes(
            self.pyboy.memory[ADDR_PLAYER_X : ADDR_PLAYER_X + 2], "little"
        )
        in_level = self.pyboy.memory[ADDR_MODE] == MODE_LEVEL
        if in_level:
            if not self._stuck_in_level:
                self._stuck_last_progress = self.level_progress
                self.stuck_frames = 0
                self.stuck = False
                self._stuck_in_level = True
            elif abs(self.level_progress - self._stuck_last_progress) > MAX_PROGRESS_DELTA_PER_FRAME:
                # The camera coordinate wraps at the left boundary; ignore
                # that impossible one-frame jump when measuring movement.
                pass
            elif self.level_progress == self._stuck_last_progress:
                self.stuck_frames += 1
                self.stuck = self.stuck_frames >= STUCK_TIMEOUT_FRAMES
            else:
                self._stuck_last_progress = self.level_progress
                self.stuck_frames = 0
                self.stuck = False
        else:
            self._stuck_in_level = False
            self.stuck_frames = 0
            self.stuck = False
        if self.pyboy.memory[ADDR_MODE] == MODE_LEVEL:
            self.custom_next_level_prepared = False

    def reset_game(self, timer_div=None):
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self.stuck = False
        self.stuck_frames = 0
        self._stuck_last_progress = self.level_progress
        self._stuck_in_level = self.pyboy.memory[ADDR_MODE] == MODE_LEVEL

    def _game_area_tiles(self):
        """Return interaction types for the camera-relative background map."""
        if self._tile_cache_invalid:
            if self.metatile_interaction_types is None:
                self.metatile_interaction_types = np.asarray(
                    self.pyboy.memory[
                        INTERACTION_TABLE_BANK, INTERACTION_TABLE_ADDRESS : INTERACTION_TABLE_ADDRESS + 0x100
                    ],
                    dtype=np.uint32,
                )
            xx, yy, width, height = self.game_area_section
            tiles = np.zeros((height, width), dtype=np.uint32)
            camera_x = self._camera_x()
            for y in range(height):
                for x in range(width):
                    world_x = camera_x + (xx + x) * 8
                    world_y = (yy + y) * 8
                    metatile_x = world_x // 16
                    metatile_y = world_y // 16
                    if not (0 <= metatile_x < METATILE_MAP_WIDTH * 2 and 0 <= metatile_y < METATILE_MAP_HEIGHT):
                        continue
                    screen = metatile_x // METATILE_SCREEN_WIDTH
                    bank = METATILE_MAP_BANK + screen // 16
                    address = (
                        METATILE_MAP_ADDRESS
                        + (screen % 16) * METATILE_SCREEN_SIZE
                        + metatile_y * METATILE_SCREEN_WIDTH
                        + metatile_x % METATILE_SCREEN_WIDTH
                    )
                    metatile = self.pyboy.memory[bank, address]
                    tiles[y, x] = self.metatile_interaction_types[metatile]
            self._cached_game_area_tiles = tiles
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the camera-relative background interaction types with sprites overlaid.

        Background values are the stable interaction codes used by the game,
        rather than graphics-dependent 8x8 VRAM tile IDs. The codes are
        defined by ``Tile16_InteractTypes`` in the game's ROM.
        """
        tiles_matrix = self.game_area_background()
        sprites = self._sprites_on_screen()
        xx, yy, width, height = self.game_area_section
        camera_y = self._camera_y()
        for sprite in sprites:
            x = ((sprite.x + 4) // 8) - xx
            y = ((sprite.y + camera_y + 4) // 8) - yy
            sprite_value = self.mapping[sprite.tile_identifier] + self.sprite_offset
            if 0 <= x < width and 0 <= y < height and self.mapping[sprite.tile_identifier] != 0:
                tiles_matrix[y, x] = sprite_value
            if len(sprite.tiles) == 2 and 0 <= x < width and 0 <= y + 1 < height:
                if self.mapping[sprite.tile_identifier + 1] != 0:
                    tiles_matrix[y + 1, x] = self.mapping[sprite.tile_identifier + 1] + self.sprite_offset
        return tiles_matrix

    def game_area_background(self):
        """Return the mapped background without sprite overlays."""
        return background_mapping_minimal[np.asarray(self._game_area_tiles(), dtype=np.uint32)]

    def _camera_x(self):
        return int.from_bytes(self.pyboy.memory[ADDR_CAMERA_X_LOW : ADDR_CAMERA_X_HIGH + 1], "little")

    def _camera_y(self):
        return self.pyboy.memory[ADDR_CAMERA_Y]

    def _press(self, button):
        self.pyboy.button_press(button)
        for _ in range(20):
            self.pyboy.tick(1, False)
        self.pyboy.button_release(button)

    def _wait_for_mode(self, *modes, spam_start=False, settle_frames=20):
        while self.pyboy.memory[ADDR_MODE] not in modes:
            if spam_start:
                self.pyboy.button("start")
            self.pyboy.tick(4, False)
        if settle_frames:
            self.pyboy.tick(settle_frames, False)

    def set_lives_left(self, amount):
        """Set Mario's lives to a value between 0 and 99."""
        if not 0 <= amount <= 99:
            raise PyBoyInvalidInputException(f"{amount} is out of bounds. Only values between 0 and 99 allowed.")
        self.pyboy.memory[ADDR_LIVES_LEFT] = amount

    def set_time_left(self, time):
        """Set the level timer to a value between 0 and 999."""
        if not 0 <= time <= 999:
            raise PyBoyInvalidInputException(f"{time} is out of bounds. Only values between 0 and 999 allowed.")
        self.pyboy.memory[ADDR_TIME_LEFT : ADDR_TIME_LEFT + 2] = time.to_bytes(2, "little")

    def set_level(self, level, super_player_levels=False):
        """
        Select a level for the game's debug level selector.

        ``super_player_levels=False`` selects Super Mario Bros.;
        ``super_player_levels=True`` selects For Super Players.
        """
        if not 0 <= level <= 0x63:
            raise PyBoyInvalidInputException(f"{level} is out of bounds. Only values between 0 and 99 allowed.")
        if not isinstance(super_player_levels, bool):
            raise PyBoyInvalidInputException("super_player_levels must be a boolean.")
        self.pyboy.memory[ADDR_LEVEL_SET] = int(super_player_levels)
        self.pyboy.memory[ADDR_SUBLEVEL] = level
        self.pyboy.memory[ADDR_LEVEL] = level
        self.selected_level = level
        self.selected_super_player_levels = super_player_levels
        self.level_selected = True

    def set_world_level(self, world, level, super_player_levels=False):
        """
        Select a world and level to start from.

        World and level numbers are one-based, matching the game's display.
        The standard game has worlds 1-8 with four levels each.
        """
        if not 1 <= world <= 13:
            raise PyBoyInvalidInputException(f"{world} is out of bounds. Only worlds 1 through 13 are allowed.")
        if not 1 <= level <= 4:
            raise PyBoyInvalidInputException(f"{level} is out of bounds. Only levels 1 through 4 are allowed.")
        if not super_player_levels and world > 8:
            raise PyBoyInvalidInputException("Worlds 9 through 13 are only available in the For Super Players set.")
        self.set_level((world - 1) * 4 + level - 1, super_player_levels)

    def start_game(
        self,
        timer_div=None,
        world_level=None,
        level=None,
        super_player_levels=False,
        challenge=False,
        unlock_level_select=False,
    ):
        """
        Start a game from the title screen.

        ``world_level`` selects a one-based ``(world, level)`` tuple, matching
        Super Mario Land. ``level`` remains available for selecting a raw
        Deluxe level ID. Normal gameplay is the default; ``challenge=True``
        uses the game's Challenge selector.
        ``unlock_level_select=True`` is retained as an alias for entering the
        Challenge selector without launching a level.
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset' instead.")
        if world_level is not None and level is not None:
            raise PyBoyInvalidInputException("Specify either world_level or level, not both.")
        challenge = challenge or unlock_level_select
        if world_level is not None:
            self.set_world_level(*world_level, super_player_levels=super_player_levels)
        elif level is not None:
            self.set_level(level, super_player_levels)

        self._wait_for_mode(MODE_TITLE_SCREEN, spam_start=True)
        self._wait_for_mode(MODE_MAIN_MENU, spam_start=True)

        if challenge:
            self.pyboy.memory[ADDR_MENU_SELECTION] = 1
            self._press("a")
            self._wait_for_mode(MODE_CHALLENGE_SELECT)
            self.pyboy.memory[ADDR_CHALLENGE_UNLOCK] = 1

            if self.level_selected and not unlock_level_select:
                self.set_level(self.selected_level, self.selected_super_player_levels)
                self._press("a")
                self._wait_for_mode(MODE_WORLD_MAP)
                self._press("start")
                self._wait_for_mode(MODE_LEVEL)
        else:
            if self.level_selected:
                self.pyboy.memory[ADDR_MODE] = MODE_DEBUG_INIT
                self._wait_for_mode(MODE_DEBUG_MENU)
                self.pyboy.memory[ADDR_LEVEL_SET] = int(self.selected_super_player_levels)
                self.pyboy.memory[ADDR_SUBLEVEL] = self.selected_level
                self._press("a")
            else:
                self._press("a")
                self._wait_for_mode(MODE_FILE_SELECT)
                self._press("a")
                self._wait_for_mode(MODE_WORLD_MAP)
                self._press("start")
            self._wait_for_mode(MODE_LEVEL)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)
        self.custom_level_sequence_index = -1
        if not challenge and not super_player_levels:
            current_world_level = (
                int(self.pyboy.memory[ADDR_LEVEL] // 4 + 1),
                int(self.pyboy.memory[ADDR_LEVEL] % 4 + 1),
            )
            if current_world_level in CUSTOM_LEVEL_SEQUENCE:
                self.custom_level_sequence_index = CUSTOM_LEVEL_SEQUENCE.index(current_world_level)
        self.custom_next_level_prepared = False

    def game_over(self):
        return self.pyboy.memory[ADDR_PLAYER_STATE] == 3 or self.pyboy.memory[ADDR_MODE] in (
            0x0E,
            0x10,
            0x11,
            0x14,
            0x1B,
        )

    def __repr__(self):
        return (
            f"Super Mario Bros. Deluxe: World {'-'.join(str(i) for i in self.world)}\n"
            f"Coins: {self.coins}\n"
            f"Lives left: {self.lives_left}\n"
            f"Score: {self.score}\n"
            f"Time left: {self.time_left}\n"
            f"Level progress: {self.level_progress}\n" + super().__repr__()
        )
