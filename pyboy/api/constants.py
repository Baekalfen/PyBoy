#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
Memory constants used internally to calculate tile and tile map addresses.
"""

VRAM_OFFSET = 0x8000
"""
Start address of VRAM
"""
LCDC_OFFSET = 0xFF40
"""
LCDC Register
"""
OAM_OFFSET = 0xFE00
"""
Start address of Object-Attribute-Memory (OAM)
"""
LOW_TILEMAP = 0x1800 + VRAM_OFFSET
"""
Start address of lower tilemap
"""
HIGH_TILEMAP = 0x1C00 + VRAM_OFFSET
"""
Start address of high tilemap
"""
LOW_TILEDATA = VRAM_OFFSET
"""
Start address of lower tile data
"""
LOW_TILEDATA_NTILES = 0x100
"""
Number of tiles in lower tile data
"""
HIGH_TILEDATA = 0x800 + VRAM_OFFSET
"""
Start address of high tile data
"""
TILES = 384
"""
Number of tiles supported on Game Boy DMG (non-color)
"""
TILES_CGB = 768
"""
Number of tiles supported on Game Boy Color
"""
SPRITES = 40
"""
Number of sprites supported
"""
ROWS = 144
"""
Rows (horizontal lines) on the screen
"""
COLS = 160
"""
Columns (vertical lines) on the screen
"""
