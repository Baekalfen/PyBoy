'''
Memory addresses and descriptions taken from 
https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
'''

from enum import Enum

class SpriteBaseAddrs(Enum):
    PLAYER_SPRITE = 0xC100 # Player is ALWAYS sprite 0
    SPRITE_1 = 0xC110
    SPIRITE_2 = 0xC120
    SPRITE_3 = 0xC130
    SPRITE_4 = 0xC140
    SPRITE_5 = 0xC150
    SPRITE_6 = 0xC160
    SPRITE_7 = 0xC170
    SPRITE_8 = 0xC180
    SPRITE_9 = 0xC190
    SPRITE_10 = 0xC1A0
    SPRITE_11 = 0xC1B0
    SPRITE_12 = 0xC1C0
    SPRITE_13 = 0xC1D0
    SPRITE_14 = 0xC1E0
    SPRITE_15 = 0xC1F0

class SpriteMemoryOffsets(Enum):
    PICTURE_ID = 0x0
    MOVEMENT_STATUS = 0x1 # (0: uninitialized, 1: ready, 2: delayed, 3: moving)
    # TODO: Figure out exactly what this data looks like
    IMAGE_INDEX = 0x2 # (changed on update, $ff if off screen, includes facing direction, progress in walking animation and a sprite-specific offset)
    Y_SCREEN_POS_D = 0x3 # Y screen position delta (-1,0 or 1; added to c1x4 on each walking animation update)
    Y_SCREEN_POS = 0x4 # Y screen position (in pixels, always 4 pixels above grid which makes sprites appear to be in the center of a tile)
    X_SCREEN_POS_D = 0x5 # X screen position delta (-1,0 or 1; added to c1x6 on each walking animation update)
    X_SCREEN_POS = 0x6 # X screen position (in pixels, snaps to grid if not currently walking)
    INTRA_ANIMATION_FRAME_COUNTER = 0x7 # intra-animation-frame counter (counting upwards to 4 until c1x8 is incremented)
    ANIMATION_FRAME_COUNTER = 0x8 # animation frame counter (increased every 4 updates, hold four states (totalling to 16 walking frames)
    FACING_DIRECTION = 0x9 # facing direction (0: down, 4: up, 8: left, $c: right)

