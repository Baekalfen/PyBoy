#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger

cdef int TILES
cdef int ROOM_TABLE_BANK, ROOM_TABLE_ADDR, ROOM_BYTES, ROOM_COUNT, ROOM_SIDE
cdef int TUTORIAL_PAIRS, TUTORIAL_END
cdef int INTERMEDIATE_START, INTERMEDIATE_PER_FLOOR
cdef int ADVANCED_START, ADVANCED_PER_FLOOR, PRO_START
cdef int ROOM_NUMBER_ADDR, FLOOR_ADDR, LEVEL_IN_FLOOR_ADDR
cdef int HEARTS_LEFT_ADDR, MAGIC_SHOTS_ADDR, SCENE_ADDR, BOARD_ADDR
cdef int OAM_BUFFER_ADDR, OAM_BUFFER_BYTES, LOLO_SPRITE_BYTES
cdef int SCENE_PLAYING, SCENE_TUTORIAL_DEMO, LOAD_ROOM_READ, ROM_BANK
cdef int CODE_LOLO, CODE_TREE, CODE_ROCK, CODE_RIVER_MIN, CODE_RIVER_MAX, CODE_FLOOR
cdef int CODE_BRIDGE_MIN, CODE_BRIDGE_MAX, CODE_ONE_WAY_MIN, CODE_ONE_WAY_MAX
cdef int CODE_FRAMER, CODE_HEART, CODE_MAGIC_HEART, CODE_DESERT
cdef int CODE_BREAK_TILE_MIN, CODE_BREAK_TILE_MAX, CODE_FLOWER_BED, CODE_DOOR
cdef int CODE_MARKER_MIN, CODE_MARKER_MAX, CODE_BREAK_TILE
cdef int CODE_ENEMY_MIN, CODE_ENEMY_MAX, CODE_ENEMY, CODE_DOOR_OPEN
cdef tuple ENEMY_NAMES, BOOT_STORY_ALTERNATIVES
cdef dict CELL_GLYPHS
cdef int PRESS_TICKS, HALF_STEP_TICKS, SHOOT_TICKS
cdef int SETTLE_MAX_TICKS, SETTLE_STABLE_TICKS, SETTLE_MIN_TICKS
cdef int BOOT_TITLE_TICKS, BOOT_MENU_TICKS, BOOT_STORY_TICKS, BOOT_ROOM_TICKS
cdef int BOOT_MAX_ROOM_PRESSES


cdef class GameWrapperAdventuresOfLolo(PyBoyGameWrapper):
    cdef readonly int room
    cdef readonly int floor
    cdef readonly int level_in_floor
    cdef readonly int hearts_left
    cdef readonly int magic_shots
    cdef readonly tuple lolo
    cdef readonly tuple door
    cdef readonly bint life_lost

    cdef int _tile_heart
    cdef int _tile_framer
    cdef int _tile_door_closed
    cdef int _tile_door_open
    cdef list _forced_room
    cdef bint _hook_registered
    cdef int _last_hearts
    cdef int _last_room

    cpdef list enemies(self)
    cpdef list hearts(self)
    cpdef list framers(self)
    cpdef list rooms(self)
    cpdef tuple room_layout(self, index)

    cpdef int start_game(self, timer_div=*, room=*, magic_shots=*) except -1
