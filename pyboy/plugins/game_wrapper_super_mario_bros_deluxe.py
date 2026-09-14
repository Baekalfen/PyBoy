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
SPRITE_SLOT_COUNT = 0x0F
SPRITE_WRAM_BANK = 1
ADDR_SPRITE_STATUS = 0xD000
ADDR_SPRITE_ID = 0xD00F
ADDR_SPRITE_X_LOW = 0xD01E
ADDR_SPRITE_X_HIGH = 0xD02D
ADDR_SPRITE_Y_LOW = 0xD03C
ADDR_SPRITE_Y_HIGH = 0xD04B
ADDR_SPRITE_X_SPEED = 0xD05A
ADDR_SPRITE_Y_SPEED = 0xD069
ADDR_SPRITE_SUBSTATE = 0xD186
SPRITE_SLOT_FIELDS = (
    ("status", ADDR_SPRITE_STATUS),
    ("id", ADDR_SPRITE_ID),
    ("x_low", ADDR_SPRITE_X_LOW),
    ("x_high", ADDR_SPRITE_X_HIGH),
    ("y_low", ADDR_SPRITE_Y_LOW),
    ("y_high", ADDR_SPRITE_Y_HIGH),
    ("x_speed_raw", ADDR_SPRITE_X_SPEED),
    ("y_speed_raw", ADDR_SPRITE_Y_SPEED),
    ("d078", 0xD078),
    ("d087", 0xD087),
    ("d096", 0xD096),
    ("d0a5", 0xD0A5),
    ("d0b4", 0xD0B4),
    ("d0c3", 0xD0C3),
    ("d0d2", 0xD0D2),
    ("d0e1", 0xD0E1),
    ("d0f0", 0xD0F0),
    ("d0ff", 0xD0FF),
    ("d10e", 0xD10E),
    ("d11d", 0xD11D),
    ("d12c", 0xD12C),
    ("d13b", 0xD13B),
    ("d14a", 0xD14A),
    ("d159", 0xD159),
    ("d168", 0xD168),
    ("d177", 0xD177),
    ("substate", ADDR_SPRITE_SUBSTATE),
    ("d195", 0xD195),
    ("d1a4", 0xD1A4),
    ("d1b3", 0xD1B3),
    ("d1c2", 0xD1C2),
    ("d1d1", 0xD1D1),
    ("d1e0", 0xD1E0),
    ("d1ef", 0xD1EF),
    ("d1fe", 0xD1FE),
    ("d20d", 0xD20D),
    ("d21c", 0xD21C),
    ("d22b", 0xD22B),
    ("d23a", 0xD23A),
    ("d249", 0xD249),
    ("d258", 0xD258),
    ("d267", 0xD267),
    ("d276", 0xD276),
    ("d285", 0xD285),
    ("d294", 0xD294),
    ("d2a3", 0xD2A3),
    ("d2b2", 0xD2B2),
    ("d2c1", 0xD2C1),
    ("d2d0", 0xD2D0),
)

MARIO_FIREBALL_ID = 0x0D
FIREBAR_ID_MIN = 0x0F
FIREBAR_ID_MAX = 0x16

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
    [38, 39, *range(68, 74), *range(84, 92), *range(96, 100), 138, 139, *range(176, 184), *range(186, 190)]
] = 0
mapping_minimal[[132, 133, 168, 169, 170, 171]] = 0  # Castle

mapping_minimal[[*range(0, 8), *range(16, 24), *range(384, 392)]] = 1  # Mario
mapping_minimal[[128, 129, 130, 131, 136, 137]] = 8  # Brick
mapping_minimal[[*range(52, 56)]] = 7  # Goomba
mapping_minimal[[100, 101]] = 14  # Star
mapping_minimal[[48, 49, *range(80, 84)]] = 15  # End of game flag
mapping_minimal[[*range(92, 96)]] = 12  # Mario fireball (and Rotating flames!!!)
mapping_minimal[[*range(194, 198)]] = 18  # Rotating flames
mapping_minimal[[46, 47, *range(114, 118)]] = 11  # Flower
mapping_minimal[[*range(56, 68)]] = 13  # Turtle
mapping_minimal[[42, 43, 44, 45]] = 9  # Mushroom
mapping_minimal[[34, 35, 124, 125, 126, 127]] = 10  # Plant
mapping_minimal[[414, 415, 416, 417, 418, 419, 482, 483]] = 16  # Trampoline
mapping_minimal[[474, 475, 476, 477, 478, 479, 480, 481]] = 17  # Flying turtle

mapping_minimal[[*range(28, 34)]] = 0  # Mario fireball explosion
mapping_minimal[[*range(56, 68)]] = 19  # Turtle
mapping_minimal[[*range(108, 114)]] = 20  # Bowser flame
mapping_minimal[[428, 429]] = 21  # Platform
mapping_minimal[[*range(496, 512), *range(400, 410)]] = 22  # Bowser
mapping_minimal[[422, 423, 424, 425, 426, 427]] = 23  # Squid
mapping_minimal[[74, 75, 76, 77, 78, 79]] = 24  # Fish
mapping_minimal[[26, 27]] = 25  # Lava fireball (also 28, but it conflicts)

mapping_minimal[
    [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 160, 161, 162, 163, 164, 165, 166, 167]
] = 26  # Hammer guy
mapping_minimal[[*range(102, 108)]] = 27  # hammers

mapping_minimal[[438, 439, 440, 441, 442, 443, 444, 445]] = 28  # Beetle

mapping_minimal[[*range(456, 464)]] = 28  # Red spiky thing
mapping_minimal[[*range(464, 468)]] = 29  # Falling red spiky thing
mapping_minimal[[*range(448, 456)]] = 30  # Man in cloud
mapping_minimal[[*range(470, 474)]] = 31  # Bullet

object_id_mapping = np.zeros(0x65, dtype=np.uint32)
object_id_mapping[0] = 0  # Inactive
object_id_mapping[0x01] = 0  # BounceSpr01
object_id_mapping[[0x02, 0x03, 0x31]] = 19  # KoopaBuzzy
object_id_mapping[0x04] = 7  # Goomba
object_id_mapping[[*range(0x05, 0x09)]] = 24  # CheepCheepSwimming
object_id_mapping[0x09] = 15  # FlagpoleSpr
object_id_mapping[0x0A] = 0  # CastleFlag
object_id_mapping[0x0B] = 0  # CoinFromBlock
object_id_mapping[0x0C] = 0  # ItemFromBlock
object_id_mapping[0x0D] = 12  # MarioFireball
object_id_mapping[0x0E] = 8  # BrokenBrick
object_id_mapping[[*range(0x0F, 0x17)]] = 18  # Firebar
object_id_mapping[0x17] = 26  # HammerBro
object_id_mapping[0x18] = 27  # Hammer
object_id_mapping[0x19] = 10  # PiranhaUp
object_id_mapping[0x1A] = 22  # Bowser
object_id_mapping[0x1B] = 20  # BowserFire
object_id_mapping[0x1C] = 0  # ToadPeach
object_id_mapping[0x1D] = 0  # Spr1D
object_id_mapping[0x1E] = 0  # Spr1E
object_id_mapping[0x1F] = 25  # Podoboo
object_id_mapping[0x20] = 0  # VineSpr
object_id_mapping[0x21] = 0  # Firework
object_id_mapping[0x22] = 0  # Spr22
object_id_mapping[0x23] = 0  # Spr23
object_id_mapping[0x24] = 0  # BulletBillShooter
object_id_mapping[0x25] = 31  # BulletBill
object_id_mapping[[*range(0x26, 0x2C)]] = 17  # Paratroopa
object_id_mapping[0x2C] = 23  # Blooper
object_id_mapping[0x2D] = 16  # Trampoline
object_id_mapping[0x2E] = 30  # Lakitu
object_id_mapping[0x2F] = 28  # SpinyEgg
object_id_mapping[0x30] = 28  # SPiny
object_id_mapping[0x32] = 0  # BowserFireGen
object_id_mapping[0x33] = 0  # Spr33
object_id_mapping[0x34] = 0  # Spr34
object_id_mapping[0x35] = 0  # Spr35
object_id_mapping[0x36] = 0  # BulletBillGen
object_id_mapping[0x37] = 0  # Spr37
object_id_mapping[0x38] = 0  # Spr38
object_id_mapping[[*range(0x39, 0x3C)]] = 0  # ScrollCmd
object_id_mapping[0x3C] = 0  # Spr3C
object_id_mapping[0x3D] = 0  # Return027A75
object_id_mapping[0x3E] = 0  # Spr3E
object_id_mapping[0x3F] = 0  # Spr3F
object_id_mapping[0x40] = 0  # Empty06658E
object_id_mapping[0x41] = 0  # Spr41
object_id_mapping[0x42] = 0  # RaceCountdown
object_id_mapping[0x43] = 0  # Spr43
object_id_mapping[0x44] = 0  # Spr44
object_id_mapping[0x45] = 0  # CloudBonusPerfect
object_id_mapping[0x46] = 0  # Boo
object_id_mapping[0x47] = 10  # PiranhaDown
object_id_mapping[0x48] = 0  # Spr48
object_id_mapping[[*range(0x49, 0x4D)]] = 0  # MultiKoopaGoomba
object_id_mapping[0x4D] = 16  # TrampolineGreen
object_id_mapping[[0x4E, 0x4F]] = 0  # MultiParatroopa
object_id_mapping[[*range(0x50, 0x56)]] = 0  # ElevatorGen
object_id_mapping[[*range(0x56, 0x60)]] = 21  # MovingPlatform
object_id_mapping[[*range(0x60, 0x64)]] = 21  # ScaleLift
object_id_mapping[0x64] = 21  # MovingPlatform


# mapping_minimal  has 527 unmapped indexes (entries still mapping to themselves):
# 1,
# 8–15,
# 24–25,
# 36–37,
# 40–41,
# 50–51,
# 118–123,
# 134–135,
# 140–143,
# 156–159,
# 172–175,
# 184–185,
# 190–193,
# 198–383,
# 392–399,
# 410–413,
# 420–421,
# 430–437,
# 446–447,
# 468–473,
# 484–495,
# 512–767

mapping_compressed = mapping_minimal

background_mapping_minimal = np.full(0x17, 3, dtype=np.uint32)
background_mapping_minimal[0] = 0
background_mapping_minimal[2] = 2
background_mapping_minimal[[5, 9, 10]] = 4
background_mapping_minimal[[4, 11, 19]] = 5
background_mapping_minimal[[6, 20, 22]] = 6
# background_mapping_minimal[[*range(334,342)]] = 7 # Canon


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
    object_id_mapping = object_id_mapping

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
        self.custom_level_sequence = None
        self.custom_level_sequence_index = -1
        self.custom_next_level_prepared = False
        super().__init__(*args, game_area_section=(0, 6, 20, 26), game_area_follow_scxy=False, **kwargs)
        self.metatile_interaction_types = None
        self.mapping = mapping_minimal

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        if (
            self.custom_level_sequence is not None
            and self.pyboy.memory[ADDR_MODE] == MODE_OVERWORLD_INIT
            and not self.custom_next_level_prepared
        ):
            if 0 <= self.custom_level_sequence_index < len(self.custom_level_sequence) - 1:
                next_world, next_level = self.custom_level_sequence[self.custom_level_sequence_index + 1]
                next_level_id = (next_world - 1) * 4 + next_level - 1
                self.pyboy.memory[ADDR_LEVEL_SET] = 0
                self.pyboy.memory[ADDR_SUBLEVEL] = next_level_id
                self.pyboy.memory[ADDR_LEVEL] = next_level_id
                self.custom_level_sequence_index += 1
                self.custom_next_level_prepared = True

        self.level = self.pyboy.memory[ADDR_LEVEL]
        self.world = (int(self.level // 4 + 1), int(self.level % 4 + 1)) if self.level < 0x20 else (0, int(self.level))
        self.mapping = mapping_minimal
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

    def object_slots(self):
        """Return active game objects with WRAM data and game-area coordinates."""
        objects = []
        section_x, section_y, _, _ = self.game_area_section
        camera_x = self._camera_x()
        camera_y = self._camera_y()
        for slot in range(SPRITE_SLOT_COUNT):
            values = {name: self.pyboy.memory[SPRITE_WRAM_BANK, address + slot] for name, address in SPRITE_SLOT_FIELDS}
            if values["status"] == 0:
                continue
            x = values["x_low"] | values["x_high"] << 8
            y = values["y_low"] | values["y_high"] << 8
            x_speed = values["x_speed_raw"]
            y_speed = values["y_speed_raw"]
            game_area_x = ((x - camera_x + 4) // 8) - section_x
            game_area_y = ((y + 4) // 8) - section_y
            screen_x = x - camera_x
            screen_y = y - camera_y
            values.update(
                {
                    "slot": slot,
                    "mapped_id": int(object_id_mapping[values["id"]]),
                    "x": x,
                    "y": y,
                    "game_area_x": game_area_x,
                    "game_area_y": game_area_y,
                    "screen_x": screen_x,
                    "screen_y": screen_y,
                    "x_signed": x - 0x10000 if x & 0x8000 else x,
                    "y_signed": y - 0x10000 if y & 0x8000 else y,
                    "x_speed": x_speed - 0x100 if x_speed & 0x80 else x_speed,
                    "y_speed": y_speed - 0x100 if y_speed & 0x80 else y_speed,
                }
            )
            objects.append(values)
        return objects

    def game_area_annotations(self):
        annotations = [
            (
                obj["screen_x"],
                obj["screen_y"],
                f"s{obj['slot']} i{obj['id']:02X} m{obj['mapped_id']}",
            )
            for obj in self.object_slots()
        ]
        player_x = int.from_bytes(self.pyboy.memory[ADDR_PLAYER_X : ADDR_PLAYER_X + 2], "little")
        player_y = self.pyboy.memory[ADDR_PLAYER_Y]
        annotations.append(
            (
                player_x - self._camera_x(),
                player_y - self._camera_y(),
                "MARIO m1",
            )
        )
        return annotations

    def _fireball_mapping(self, sprite, objects):
        if not 92 <= sprite.tile_identifier < 96:
            return 0

        world_x = sprite.x + self._camera_x()
        world_y = sprite.y + self._camera_y()
        for obj in objects:
            if obj["id"] != MARIO_FIREBALL_ID:
                continue
            if abs(world_x - obj["x"]) <= 8 and abs(world_y - obj["y"]) <= 8:
                return 12

        if any(FIREBAR_ID_MIN <= obj["id"] <= FIREBAR_ID_MAX for obj in objects):
            return 18
        return 0

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
        ambiguous_sprites = [sprite for sprite in sprites if 92 <= sprite.tile_identifier < 96]
        objects = self.object_slots() if ambiguous_sprites else ()
        xx, yy, width, height = self.game_area_section
        camera_y = self._camera_y()
        for sprite in sprites:
            x = ((sprite.x + 4) // 8) - xx
            y = ((sprite.y + camera_y + 4) // 8) - yy
            tile_identifier = sprite.tile_identifier
            fireball_mapping = self._fireball_mapping(sprite, objects)
            sprite_mapping = fireball_mapping or self.mapping[tile_identifier]
            sprite_value = sprite_mapping + self.sprite_offset
            if 0 <= x < width and 0 <= y < height and self.mapping[tile_identifier] != 0:
                tiles_matrix[y, x] = sprite_value
            if len(sprite.tiles) == 2 and 0 <= x < width and 0 <= y + 1 < height:
                second_mapping = fireball_mapping or self.mapping[tile_identifier + 1]
                if second_mapping != 0:
                    tiles_matrix[y + 1, x] = second_mapping + self.sprite_offset
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
        custom_level_sequence=None,
    ):
        """
        Start a game from the title screen.

        ``world_level`` selects a one-based ``(world, level)`` tuple, matching
        Super Mario Land. ``level`` remains available for selecting a raw
        Deluxe level ID. Normal gameplay is the default; ``challenge=True``
        uses the game's Challenge selector.
        ``unlock_level_select=True`` is retained as an alias for entering the
        Challenge selector without launching a level.
        ``custom_level_sequence`` optionally overrides the normal level order
        with a sequence of one-based ``(world, level)`` tuples.
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset' instead.")
        if world_level is not None and level is not None:
            raise PyBoyInvalidInputException("Specify either world_level or level, not both.")
        if custom_level_sequence is not None:
            normalized_sequence = []
            for sequence_world_level in custom_level_sequence:
                normalized_sequence.append(tuple(sequence_world_level))
            custom_level_sequence = tuple(normalized_sequence)
            if not custom_level_sequence:
                raise PyBoyInvalidInputException("custom_level_sequence must not be empty.")
            for sequence_world_level in custom_level_sequence:
                if len(sequence_world_level) != 2:
                    raise PyBoyInvalidInputException("custom_level_sequence entries must be (world, level) tuples.")
                sequence_world, sequence_level = sequence_world_level
                if not 1 <= sequence_world <= 13:
                    raise PyBoyInvalidInputException(
                        f"{sequence_world} is out of bounds. Only worlds 1 through 13 are allowed."
                    )
                if not 1 <= sequence_level <= 4:
                    raise PyBoyInvalidInputException(
                        f"{sequence_level} is out of bounds. Only levels 1 through 4 are allowed."
                    )
                if not super_player_levels and sequence_world > 8:
                    raise PyBoyInvalidInputException(
                        "Worlds 9 through 13 are only available in the For Super Players set."
                    )
        self.custom_level_sequence = custom_level_sequence
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
        if self.custom_level_sequence is not None and not challenge and not super_player_levels:
            current_world_level = (
                int(self.pyboy.memory[ADDR_LEVEL] // 4 + 1),
                int(self.pyboy.memory[ADDR_LEVEL] % 4 + 1),
            )
            if current_world_level in self.custom_level_sequence:
                self.custom_level_sequence_index = self.custom_level_sequence.index(current_world_level)
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
