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

# Pending screen captures. CHR_TRN, PCT_TRN and PAL_TRN all deliver their
# payload as pixels drawn on the LCD; the SGB captures the finished frame
# a few frames after the command.
CAPTURE_OFF = 0
CAPTURE_CHR_LOW = 1
CAPTURE_CHR_HIGH = 2
CAPTURE_PCT = 3
CAPTURE_PAL = 4

# Frames between a transfer command and the screen capture
CAPTURE_DELAY_FRAMES = 3

# PCT_TRN payload: a 32x32 tile map followed by 4 palettes of 16 colors
BORDER_MAP_WORDS = 32 * 32
BORDER_PALETTE_WORDS = 4 * 16


def _screen_row_2bpp(screenbuffer, rgb_to_index, x_start, y):
    """Pack 8 screen pixels starting at (x_start, y) into one 2bpp tile row.

    A 2bpp tile row is two bytes: the first holds color bit 0 of each
    pixel, the second holds color bit 1, with the leftmost pixel in the
    most significant bit of each byte.
    """
    plane0 = 0
    plane1 = 0
    for x in range(8):
        color = rgb_to_index.get(screenbuffer[y, x_start + x], 0) & 3
        plane0 |= (color & 1) << (7 - x)
        plane1 |= (color >> 1) << (7 - x)
    return plane0, plane1


class SGBState:
    """Tracks the state of SGB command processing."""

    def __init__(self):
        self.sgb_detected = False
        self.multiplayer_enabled = False
        self.multiplayer_players = 1
        self.mask_mode = 0  # 0=normal, 1=freeze, 2=black, 3=color0

        # Border-related state
        self.border_enabled = False
        # 4bpp tiles: 256 tiles * 32 bytes each = 8192 bytes
        # Low CHR_TRN fills tiles 0-127, high CHR_TRN fills tiles 128-255
        self.border_tiles = array("B", [0] * 0x2000)
        # 32x32 tile map, each entry uint16_t = 2048 bytes
        self.border_map = array("B", [0] * 0x800)
        # 4 palettes * 16 colors * 2 bytes (RGB555) = 128 bytes
        self.border_palettes = array("B", [0] * 0x80)

        # Screen capture scheduling
        self.capture_delay = 0
        self.pending_capture = CAPTURE_OFF

        self.border_data_changed = False

        # Game's BGP color 0 (used as border background for color index 0)
        self.bg_color_0 = 0xFFFFFFFF  # default white

        # SGB command processing
        self.last_command = 0

        # Multiple joypad state
        self.joypad_data = array("B", [0xFF] * 4)
        self.current_joypad = 0


class SGB:
    """Main SGB emulation class."""

    def __init__(self, mb):
        self.mb = mb
        self.state = SGBState()
        self.enabled = False
        self.packet_buffer = array("B", [0] * SGB_PACKET_SIZE)
        self.completed_packet = array("B", [0] * SGB_PACKET_SIZE)
        self.bit_count = 0
        self.pulse_armed = False
        self.write_armed = False
        self.packet_complete = False
        self.collecting = False
        self.command_ready = False
        self.multiplayer = False
        self.player_count = 1
        self.active_player = 0

        logger.debug("SGB module initialized")

    def reset(self):
        """Reset the SGB state."""
        self.state = SGBState()
        self.state.sgb_detected = self.enabled
        self.bit_count = 0
        self.pulse_armed = False
        self.write_armed = False
        self.packet_complete = False
        self.collecting = False
        self.command_ready = False
        self.multiplayer = False
        self.player_count = 1
        self.active_player = 0

    def process_p1_write(self, value):
        """Process writes to the P1/JOYP register for SGB command packets.

        P14/P15 encode a four-level serial handshake. Level zero opens a
        packet, levels one and two carry a one or zero, and level three closes it.
        """
        if not self.enabled:
            return value

        pulse = (value >> 4) & 3

        if pulse == 3:
            if self.packet_complete and self.bit_count >= 128:
                # Keep a copy for process_command; the receive buffer is
                # cleared so a following packet cannot overwrite it before
                # the command runs at the next tick_frame.
                for i in range(16):
                    self.completed_packet[i] = self.packet_buffer[i]
                self.command_ready = True
                self.bit_count = 0
                self.pulse_armed = False
                self.write_armed = False
                self.packet_complete = False
                self.collecting = False
                for i in range(16):
                    self.packet_buffer[i] = 0
            else:
                self.pulse_armed = True

        elif pulse == 0:
            self.pulse_armed = True
            self.write_armed = True
            self.packet_complete = False
            self.bit_count = 0
            self.collecting = True
            for i in range(16):
                self.packet_buffer[i] = 0

        elif pulse == 1:
            if self.pulse_armed and self.write_armed:
                if self.bit_count < 128:
                    byte_pos = self.bit_count // 8
                    bit_pos = self.bit_count % 8
                    self.packet_buffer[byte_pos] |= 1 << bit_pos
                    self.bit_count += 1
                    self.pulse_armed = False
                    if (self.bit_count & 127) == 0:
                        self.packet_complete = True
                else:
                    self.pulse_armed = False
                    self.write_armed = False
                    self.bit_count = 0
                    self.collecting = False
                    for i in range(16):
                        self.packet_buffer[i] = 0

        elif pulse == 2:
            if self.pulse_armed and self.write_armed:
                if self.bit_count < 128:
                    self.bit_count += 1
                    self.pulse_armed = False
                    if (self.bit_count & 127) == 0:
                        self.packet_complete = True
                else:
                    self.pulse_armed = False
                    self.write_armed = False
                    self.bit_count = 0
                    self.collecting = False
                    for i in range(16):
                        self.packet_buffer[i] = 0

        return value

    def process_p1_read(self, value):
        """Process reads from the P1/JOYP register for SGB multiplayer."""
        return value

    def tick_frame(self):
        """Called once per frame.

        Dispatches a fully received command packet, and runs any pending
        screen capture once its delay has expired. The delay gives the
        game time to draw the transfer payload onto the LCD.
        """
        if not self.enabled:
            return

        if self.command_ready:
            self.command_ready = False
            self.process_command()

        # Keep the game's first background colour for transparent border pixels.
        self.state.bg_color_0 = self.mb.lcd.BGP.getcolor(0)

        if self.state.capture_delay > 0:
            self.state.capture_delay -= 1
            if self.state.capture_delay == 0:
                self._run_pending_capture()

    def _run_pending_capture(self):
        """Capture the LCD contents as SGB transfer data.

        The game renders the payload with BGP colors 0-3; the colors are
        mapped back to their color indices through the current BGP palette
        before being packed as data.
        """
        capture = self.state.pending_capture
        self.state.pending_capture = CAPTURE_OFF

        # Build reverse BGP lookup: RGB32 -> color index 0-3
        bgp = self.mb.lcd.BGP
        rgb_to_index = {}
        for i in range(4):
            rgb_to_index[bgp.lookup[i]] = i

        screenbuffer = self.mb.lcd.renderer._screenbuffer

        if capture == CAPTURE_CHR_LOW:
            self._capture_chr(screenbuffer, rgb_to_index, False)
            self.state.border_data_changed = True
        elif capture == CAPTURE_CHR_HIGH:
            self._capture_chr(screenbuffer, rgb_to_index, True)
            self.state.border_data_changed = True
        elif capture == CAPTURE_PCT:
            self._capture_pct(screenbuffer, rgb_to_index)
            self.state.border_data_changed = True
        elif capture == CAPTURE_PAL:
            # Custom system palettes are not used for border rendering.
            pass

    def _capture_chr(self, screenbuffer, rgb_to_index, high_bank):
        """Capture CHR_TRN data: 256 tiles of 2bpp tile data.

        The game draws the tiles on the 20x18 tile LCD grid, row by row,
        until 256 tiles are covered. Each 8x8 tile becomes 16 bytes.
        The low bank fills border tiles 0-127, the high bank 128-255.
        """
        tiles = self.state.border_tiles
        out = 0x1000 if high_bank else 0
        remaining = 256
        for tile_y in range(0, 144, 8):
            for tile_x in range(0, 160, 8):
                if remaining == 0:
                    return
                for row in range(8):
                    plane0, plane1 = _screen_row_2bpp(screenbuffer, rgb_to_index, tile_x, tile_y + row)
                    tiles[out] = plane0
                    tiles[out + 1] = plane1
                    out += 2
                remaining -= 1

    def _capture_pct(self, screenbuffer, rgb_to_index):
        """Capture PCT_TRN data: the border map and its palettes.

        The game draws 136 tiles (1088 16-bit words) on the LCD. The
        first 1024 words are the 32x32 border map; the last 64 words are
        four palettes of 16 RGB555 colors. Words are little-endian.
        """
        border_map = self.state.border_map
        border_palettes = self.state.border_palettes
        word_index = 0
        total_words = BORDER_MAP_WORDS + BORDER_PALETTE_WORDS
        for tile_y in range(0, 144, 8):
            for tile_x in range(0, 160, 8):
                if word_index == total_words:
                    return
                for row in range(8):
                    plane0, plane1 = _screen_row_2bpp(screenbuffer, rgb_to_index, tile_x, tile_y + row)
                    if word_index < BORDER_MAP_WORDS:
                        border_map[word_index * 2] = plane0
                        border_map[word_index * 2 + 1] = plane1
                    else:
                        palette_word = word_index - BORDER_MAP_WORDS
                        border_palettes[palette_word * 2] = plane0
                        border_palettes[palette_word * 2 + 1] = plane1
                    word_index += 1

        self.state.border_enabled = True

    def process_command(self):
        """Process the received SGB command packet."""
        command_info = self.completed_packet[0]
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
        """Handle MLT_REQ command for multiplayer support.

        The request encodes 1, 2 or 4 players. The SGB has no three-pad
        mode, so a request for three pads yields four-player mode.
        """
        requested = self.completed_packet[1] & 0x03
        players = requested + 1
        if requested == 2:
            players = 4

        self.state.multiplayer_players = players
        self.state.multiplayer_enabled = players > 1
        self.player_count = players
        self.multiplayer = players > 1

        self.state.sgb_detected = True
        self.state.current_joypad = 0
        self.active_player = 0

    def handle_pal_set(self):
        """Handle PAL_SET command for palette management."""
        pass

    def handle_chr_trn(self):
        """Handle CHR_TRN command - schedule a screen capture for tile data.

        Bit 0 of the data byte selects the tile bank: 0 fills border
        tiles 0-127, 1 fills tiles 128-255.
        """
        high_bank = self.completed_packet[1] & 0x01
        self.state.pending_capture = CAPTURE_CHR_HIGH if high_bank else CAPTURE_CHR_LOW
        self.state.capture_delay = CAPTURE_DELAY_FRAMES

    def handle_pct_trn(self):
        """Handle PCT_TRN command - schedule a screen capture for border map + palettes."""
        self.state.pending_capture = CAPTURE_PCT
        self.state.capture_delay = CAPTURE_DELAY_FRAMES

    def handle_mask_en(self):
        """Handle MASK_EN command for screen masking.

        Per the SGB protocol:
        - 0: MASK_DISABLED - normal display
        - 1: MASK_FREEZE - freeze last rendered frame
        - 2: MASK_BLACK - show all black
        - 3: MASK_COLOR_0 - show palette color 0
        """
        self.state.mask_mode = self.completed_packet[1] & 3

    def handle_obj_trn(self):
        """Handle OBJ_TRN command for SNES sprite transfer."""
        pass

    def handle_pal_trn(self):
        """Handle PAL_TRN command - schedule a screen capture for palette data."""
        self.state.pending_capture = CAPTURE_PAL
        self.state.capture_delay = CAPTURE_DELAY_FRAMES

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
            self.active_player = joypad_index

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
