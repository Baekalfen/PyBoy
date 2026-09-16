#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
Super Game Boy (SGB) emulation module.

This module implements SGB functionality including:
- SGB command packet processing
- Border support with CHR_TRN and PCT_TRN
- Multiple joypad support
- Palette management for borders
- SGB detection
"""

from array import array

import pyboy
from pyboy.utils import PyBoyException, PyBoyNotImplementedException

logger = pyboy.logging.get_logger(__name__)


class SGBException(PyBoyException):
    """Exception raised for SGB-related errors."""

    pass


class SGBNotImplementedException(PyBoyNotImplementedException):
    """Exception raised for unimplemented SGB features."""

    pass


# SGB Command Constants
# Based on https://gbdev.io/pandocs/SGB_Functions.html (SGB Command Summary)
SGB_CMD_PAL01 = 0x00  # Set SGB Palette 0,1 Data
SGB_CMD_PAL23 = 0x01  # Set SGB Palette 2,3 Data
SGB_CMD_PAL03 = 0x02  # Set SGB Palette 0,3 Data
SGB_CMD_PAL12 = 0x03  # Set SGB Palette 1,2 Data
SGB_CMD_ATTR_BLK = 0x04  # "Block" Area Designation Mode
SGB_CMD_SOUND = 0x08  # Sound On/Off
SGB_CMD_SOUND_TRN = 0x09  # Transfer Sound PRG/DATA
SGB_CMD_PAL_SET = 0x0A  # Set SGB Palette Indirect
SGB_CMD_PAL_TRN = 0x0B  # Set System Color Palette Data
SGB_CMD_ICON_EN = 0x0E  # SGB Function
SGB_CMD_DATA_SND = 0x0F  # SUPER NES WRAM Transfer 1
SGB_CMD_MLT_REQ = 0x11  # Multiplayer Request
SGB_CMD_JUMP = 0x12  # Set SNES Program Counter
SGB_CMD_CHR_TRN = 0x13  # Transfer Character Font Data
SGB_CMD_PCT_TRN = 0x14  # Set Screen Data Color Data
SGB_CMD_ATTR_TRN = 0x15  # Set Attribute from ATF
SGB_CMD_ATTR_SET = 0x16  # Set Data to ATF
SGB_CMD_MASK_EN = 0x17  # Game Boy Window Mask
SGB_CMD_OBJ_TRN = 0x18  # Super NES OBJ Mode

# SGB Packet structure
SGB_PACKET_SIZE = 16  # 16 bytes of data (128 bits)

# VRAM transfer destinations
TRANSFER_NONE = 0
TRANSFER_CHR_LOW = 1
TRANSFER_CHR_HIGH = 2
TRANSFER_PCT = 3
TRANSFER_PAL = 4


class SGBState:
    """Tracks the state of SGB command processing."""

    def __init__(self):
        self.packet_buffer = array("B", [0] * SGB_PACKET_SIZE)
        self.packet_position = 0
        self.packet_bit_position = 0
        self.receiving_packet = False
        self.current_bit = 0
        self.bits_received = 0
        self.sgb_detected = False
        self.multiplayer_enabled = False
        self.multiplayer_players = 1
        self.mask_mode = 0  # 0=normal, 1=freeze, 2=black, 3=color0

        # SameBoy-style state machine for packet bit processing
        self.ready_for_pulse = False
        self.ready_for_write = False
        self.ready_for_stop = False

        # Border-related state
        self.border_enabled = False
        # 4bpp tiles: 256 tiles * 32 bytes each = 8192 bytes
        # Low CHR_TRN fills tiles 0-127, high CHR_TRN fills tiles 128-255
        self.border_tiles = array("B", [0] * 0x2000)
        # 32x32 tile map, each entry uint16_t = 2048 bytes
        self.border_map = array("B", [0] * 0x800)
        # 4 palettes * 16 colors * 2 bytes (RGB555) = 128 bytes
        self.border_palettes = array("B", [0] * 0x80)

        # VRAM transfer countdown (SameBoy: 3 frames delay)
        self.vram_transfer_countdown = 0
        self.transfer_dest = TRANSFER_NONE

        # Flag set when new border data arrives (checked by border renderer)
        self.border_data_changed = False

        # Game's BGP color 0 (used as border background for color index 0)
        self.bg_color_0 = 0xFFFFFFFF  # default white

        # SGB command processing
        self.last_command = 0
        self.command_data = array("B", [0] * 16)

        # Multiple joypad state
        self.joypad_data = array("B", [0xFF] * 4)
        self.current_joypad = 0


class SGB:
    """Main SGB emulation class."""

    def __init__(self, mb):
        self.mb = mb
        self.state = SGBState()
        self.enabled = False
        self.bits_received = 0
        self.ready_for_pulse = False
        self.ready_for_write = False
        self.ready_for_stop = False
        self.receiving_packet = False
        self.command_pending = False
        self.multiplayer_enabled = False
        self.multiplayer_players = 1
        self.current_joypad = 0

        logger.debug("SGB module initialized")

    def reset(self):
        """Reset the SGB state."""
        self.state = SGBState()
        self.state.sgb_detected = self.enabled
        self.bits_received = 0
        self.ready_for_pulse = False
        self.ready_for_write = False
        self.ready_for_stop = False
        self.receiving_packet = False
        self.command_pending = False
        self.multiplayer_enabled = False
        self.multiplayer_players = 1
        self.current_joypad = 0

    def process_p1_write(self, value):
        """Process writes to the P1/JOYP register for SGB command packets.

        Uses SameBoy's state machine: the P1 register bits 4-5 (P14/P15) encode
        pulses: 0=start, 1=bit 1, 2=bit 0, 3=finish/idle.
        """
        if not self.enabled:
            return value

        pulse = (value >> 4) & 3

        if pulse == 3:
            if self.ready_for_stop and self.bits_received >= 128:
                self.command_pending = True
                self.bits_received = 0
                self.ready_for_pulse = False
                self.ready_for_write = False
                self.ready_for_stop = False
                self.receiving_packet = False
                for i in range(16):
                    self.packet_buffer[i] = 0
            else:
                self.ready_for_pulse = True

        elif pulse == 0:
            self.ready_for_pulse = True
            self.ready_for_write = True
            self.ready_for_stop = False
            self.bits_received = 0
            self.receiving_packet = True
            for i in range(16):
                self.packet_buffer[i] = 0

        elif pulse == 1:
            if self.ready_for_pulse and self.ready_for_write:
                if self.bits_received < 128:
                    byte_pos = self.bits_received // 8
                    bit_pos = self.bits_received % 8
                    self.packet_buffer[byte_pos] |= 1 << bit_pos
                    self.bits_received += 1
                    self.ready_for_pulse = False
                    if (self.bits_received & 127) == 0:
                        self.ready_for_stop = True
                else:
                    self.ready_for_pulse = False
                    self.ready_for_write = False
                    self.bits_received = 0
                    self.receiving_packet = False
                    for i in range(16):
                        self.packet_buffer[i] = 0

        elif pulse == 2:
            if self.ready_for_pulse and self.ready_for_write:
                if self.bits_received < 128:
                    self.bits_received += 1
                    self.ready_for_pulse = False
                    if (self.bits_received & 127) == 0:
                        self.ready_for_stop = True
                else:
                    self.ready_for_pulse = False
                    self.ready_for_write = False
                    self.bits_received = 0
                    self.receiving_packet = False
                    for i in range(16):
                        self.packet_buffer[i] = 0

        return value

    def process_p1_read(self, value):
        """Process reads from the P1/JOYP register for SGB multiplayer."""
        return value

    def tick_frame(self):
        """Called once per frame to process VRAM transfer countdown.

        SameBoy waits 3 frames after a CHR_TRN/PCT_TRN/PAL_TRN command
        before reading the screen buffer. This gives the game time to
        render the data onto the GB LCD.
        """
        if not self.enabled:
            return

        if self.command_pending:
            for i in range(SGB_PACKET_SIZE):
                self.state.packet_buffer[i] = self.packet_buffer[i]
            self.command_pending = False
            self.process_command()

        # Cache BGP color 0 for border rendering (SameBoy uses effective_palettes[0])
        self.state.bg_color_0 = self.mb.lcd.BGP.getcolor(0)

        if self.state.vram_transfer_countdown > 0:
            self.state.vram_transfer_countdown -= 1
            if self.state.vram_transfer_countdown == 0:
                self._process_vram_transfer()

    def _process_vram_transfer(self):
        """Read the GB screen buffer and convert to border data.

        The SGB protocol works by having the game render data as pixels
        on the GB LCD. The SGB reads the screen (160x144 pixels, color
        index 0-3) and converts to 2bpp tile data.

        Screen layout: 20 columns x 18 rows of 8x8 tiles.
        Each pixel (0-3) encodes 2 bits of data.
        """
        dest = self.state.transfer_dest
        self.state.transfer_dest = TRANSFER_NONE

        # Build reverse BGP lookup: RGB32 -> color index 0-3
        bgp = self.mb.lcd.BGP
        rgb_to_index = {}
        for i in range(4):
            rgb_to_index[bgp.lookup[i]] = i

        screenbuffer = self.mb.lcd.renderer._screenbuffer

        # SameBoy pixel_to_bits mapping:
        # color 0 -> 0x0000, color 1 -> 0x0080, color 2 -> 0x8000, color 3 -> 0x8080
        # Bit 7 of low byte = bitplane 0 pixel 0 (MSB first)
        # Bit 7 of high byte = bitplane 1 pixel 0
        pixel_to_bits = (0x0000, 0x0080, 0x8000, 0x8080)

        if dest == TRANSFER_CHR_LOW:
            self._read_screen_to_2bpp(screenbuffer, rgb_to_index, pixel_to_bits, 256, self.state.border_tiles, 0)
            self.state.border_data_changed = True
        elif dest == TRANSFER_CHR_HIGH:
            self._read_screen_to_2bpp(screenbuffer, rgb_to_index, pixel_to_bits, 256, self.state.border_tiles, 0x1000)
            self.state.border_data_changed = True
        elif dest == TRANSFER_PCT:
            self._read_screen_to_border(screenbuffer, rgb_to_index, pixel_to_bits)
            self.state.border_data_changed = True
        elif dest == TRANSFER_PAL:
            pass

    def _read_screen_to_2bpp(self, screenbuffer, rgb_to_index, pixel_to_bits, num_tiles, dest_array, dest_offset):
        """Read 8x8 tiles from screen buffer and convert to 2bpp data.

        Each 8x8 tile becomes 16 bytes (2 bytes per row, 2 bitplanes).
        Screen is 20 tiles wide (160 pixels).
        """
        for tile in range(num_tiles):
            tile_x = (tile % 20) * 8
            tile_y = (tile // 20) * 8
            base = dest_offset + tile * 16
            for y in range(8):
                word = 0
                py = tile_y + y
                for x in range(8):
                    px = tile_x + x
                    if px < 160 and py < 144:
                        rgb = screenbuffer[py, px]
                        color = rgb_to_index.get(rgb, 0) & 3
                        word |= pixel_to_bits[color] >> x
                dest_array[base + y * 2] = word & 0xFF
                dest_array[base + y * 2 + 1] = (word >> 8) & 0xFF

    def _read_screen_to_border(self, screenbuffer, rgb_to_index, pixel_to_bits):
        """Read PCT_TRN data: 136 tiles = 128 map tiles + 8 palette tiles.

        Map: 32x32 entries, each uint16_t (1024 entries = 2048 bytes)
        Palettes: 4 palettes x 16 colors, each uint16_t RGB555 (64 entries = 128 bytes)
        Total: 1088 uint16_t values = 136 tiles * 8 rows
        """
        all_words = [0] * (136 * 8)
        for tile in range(136):
            tile_x = (tile % 20) * 8
            tile_y = (tile // 20) * 8
            for y in range(8):
                word = 0
                py = tile_y + y
                for x in range(8):
                    px = tile_x + x
                    if px < 160 and py < 144:
                        rgb = screenbuffer[py, px]
                        color = rgb_to_index.get(rgb, 0) & 3
                        word |= pixel_to_bits[color] >> x
                all_words[tile * 8 + y] = word

        # First 1024 words = map data (32x32 entries)
        for i in range(1024):
            word = all_words[i]
            self.state.border_map[i * 2] = word & 0xFF
            self.state.border_map[i * 2 + 1] = (word >> 8) & 0xFF

        # Next 64 words = palette data (4 palettes x 16 colors)
        for i in range(64):
            word = all_words[1024 + i]
            self.state.border_palettes[i * 2] = word & 0xFF
            self.state.border_palettes[i * 2 + 1] = (word >> 8) & 0xFF

        self.state.border_enabled = True

    def process_command(self):
        """Process the received SGB command packet."""
        if len(self.state.packet_buffer) < 2:
            return

        command_info = self.state.packet_buffer[0]
        command = (command_info >> 3) & 0x1F

        self.state.last_command = command

        if command == SGB_CMD_MLT_REQ:
            self.handle_mlt_req()
        elif command == SGB_CMD_PAL_SET:
            self.handle_pal_set()
        elif command == SGB_CMD_CHR_TRN:
            self.handle_chr_trn()
        elif command == SGB_CMD_PCT_TRN:
            self.handle_pct_trn()
        elif command == SGB_CMD_MASK_EN:
            self.handle_mask_en()
        elif command == SGB_CMD_OBJ_TRN:
            self.handle_obj_trn()
        elif command == SGB_CMD_PAL_TRN:
            self.handle_pal_trn()
        elif command == SGB_CMD_ATTR_TRN:
            self.handle_attr_trn()
        elif command == SGB_CMD_ATTR_SET:
            self.handle_attr_set()
        elif command == SGB_CMD_ICON_EN:
            self.handle_icon_en()
        elif command in (
            SGB_CMD_DATA_SND,
            SGB_CMD_ATTR_BLK,
            SGB_CMD_PAL01,
            SGB_CMD_PAL23,
            SGB_CMD_PAL03,
            SGB_CMD_PAL12,
            SGB_CMD_SOUND,
            SGB_CMD_SOUND_TRN,
            SGB_CMD_JUMP,
        ):
            pass
        else:
            logger.debug("SGB: Unimplemented command 0x%02X" % command)

    def handle_mlt_req(self):
        """Handle MLT_REQ command for multiplayer support."""
        if len(self.state.packet_buffer) < 2:
            return

        player_config = self.state.packet_buffer[1] & 0x03
        players = player_config + 1

        if players == 3:
            players = 4

        self.state.multiplayer_players = players
        self.state.multiplayer_enabled = players > 1
        self.multiplayer_players = players
        self.multiplayer_enabled = players > 1

        self.state.sgb_detected = True
        self.state.current_joypad = 0
        self.current_joypad = 0

    def handle_pal_set(self):
        """Handle PAL_SET command for palette management."""
        pass

    def handle_chr_trn(self):
        """Handle CHR_TRN command - set up screen buffer transfer for tile data.

        The actual data reading happens 3 frames later via tick_frame().
        """
        if len(self.state.packet_buffer) < 2:
            return

        tile_set = self.state.packet_buffer[1] & 0x01
        self.state.transfer_dest = TRANSFER_CHR_LOW if tile_set == 0 else TRANSFER_CHR_HIGH
        self.state.vram_transfer_countdown = 3

    def handle_pct_trn(self):
        """Handle PCT_TRN command - set up screen buffer transfer for border map + palettes."""
        self.state.transfer_dest = TRANSFER_PCT
        self.state.vram_transfer_countdown = 3

    def handle_mask_en(self):
        """Handle MASK_EN command for screen masking.

        Per Pan Docs / SameBoy:
        - 0: MASK_DISABLED - normal display
        - 1: MASK_FREEZE - freeze last rendered frame
        - 2: MASK_BLACK - show all black
        - 3: MASK_COLOR_0 - show palette color 0
        """
        if len(self.state.packet_buffer) < 2:
            return
        self.state.mask_mode = self.state.packet_buffer[1] & 3

    def handle_obj_trn(self):
        """Handle OBJ_TRN command for SNES sprite transfer."""
        pass

    def handle_pal_trn(self):
        """Handle PAL_TRN command - set up screen buffer transfer for palette data."""
        self.state.transfer_dest = TRANSFER_PAL
        self.state.vram_transfer_countdown = 3

    def handle_attr_trn(self):
        """Handle ATTR_TRN command for attribute data transfer."""
        pass

    def handle_attr_set(self):
        """Handle ATTR_SET command for setting attribute data."""
        pass

    def handle_icon_en(self):
        """Handle ICON_EN command for SGB icon enable."""
        pass

    def get_border_data(self):
        """Get the current border data for rendering."""
        if not self.state.border_enabled:
            return None, None, None
        return (self.state.border_tiles, self.state.border_map, self.state.border_palettes)

    def set_joypad_data(self, joypad_index, data):
        """Set joypad data for multiplayer support."""
        if 0 <= joypad_index < 4:
            self.state.joypad_data[joypad_index] = data & 0xFF

    def set_current_joypad(self, joypad_index):
        """Set the currently selected joypad."""
        if 0 <= joypad_index < self.state.multiplayer_players:
            self.state.current_joypad = joypad_index
            self.current_joypad = joypad_index

    def save_state(self, f):
        """Save the SGB state to a file."""
        f.write(self.state.sgb_detected)
        f.write(self.state.multiplayer_enabled)
        f.write(self.state.multiplayer_players)
        f.write(self.state.mask_mode)
        f.write(self.state.border_enabled)
        f.write(self.state.last_command)
        f.write(self.state.current_joypad)

        for joypad in self.state.joypad_data:
            f.write(joypad)

        for byte in self.state.border_tiles:
            f.write(byte)
        for byte in self.state.border_map:
            f.write(byte)
        for byte in self.state.border_palettes:
            f.write(byte)

    def load_state(self, f, state_version):
        """Load the SGB state from a file."""
        if state_version < 23:
            return 0

        self.state.sgb_detected = f.read()
        self.state.multiplayer_enabled = f.read()
        self.state.multiplayer_players = f.read()
        self.state.mask_mode = f.read()
        self.state.border_enabled = f.read()
        self.state.last_command = f.read()
        self.state.current_joypad = f.read()

        for i in range(4):
            self.state.joypad_data[i] = f.read()

        for i in range(len(self.state.border_tiles)):
            self.state.border_tiles[i] = f.read()
        for i in range(len(self.state.border_map)):
            self.state.border_map[i] = f.read()
        for i in range(len(self.state.border_palettes)):
            self.state.border_palettes[i] = f.read()

    def stop(self):
        """Clean up SGB resources."""
        pass
