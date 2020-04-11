#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
Memory constants used internally to calculate tile and tile map addresses.
"""

VRAM_OFFSET = 0x8000
LCDC_OFFSET = 0xFF40
OAM_OFFSET = 0xFE00
LOW_TILEMAP = 0x1800 + VRAM_OFFSET
HIGH_TILEMAP = 0x1C00 + VRAM_OFFSET
LOW_TILEDATA = VRAM_OFFSET
LOW_TILEDATA_NTILES = 0x100
HIGH_TILEDATA = 0x800 + VRAM_OFFSET
TILES = 384
SPRITES = 40
ROWS, COLS = 144, 160
