#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
SGB API module for PyBoy.

This module provides access to Super Game Boy features and border functionality.
"""


# Keep this as a pure Python module - no Cython compilation needed
# This avoids conflicts with the core SGB module


class SGB:
    """
    API for accessing Super Game Boy features.

    This class provides access to SGB functionality including:
    - SGB detection status
    - Border control
    - Multiplayer joypad support
    - SGB command processing
    """

    def __init__(self, mb):
        """
        Initialize the SGB API.

        Args:
            mb: The motherboard instance
        """
        self.mb = mb

    @property
    def enabled(self):
        """Returns True if SGB features are enabled for the loaded cartridge."""
        return self.mb.sgb.enabled

    @property
    def detected(self):
        """Returns True if SGB hardware has been detected."""
        return self.mb.sgb.state.sgb_detected

    @property
    def border_enabled(self):
        """Returns True if an SGB border is currently active."""
        return self.mb.sgb.state.border_enabled

    @property
    def multiplayer_enabled(self):
        """Returns True if multiplayer mode is enabled."""
        return self.mb.sgb.state.multiplayer_enabled

    @property
    def multiplayer_players(self):
        """Returns the number of players in multiplayer mode."""
        return self.mb.sgb.state.multiplayer_players

    @property
    def border_data(self):
        """Returns the current border data as a tuple of (tiles, map, palettes)."""
        return self.mb.sgb.get_border_data()

    def get_border_buffer(self):
        """
        Get the current SGB border frame buffer.

        Returns:
            array: The border buffer in RGBA format (256x224)
        """
        return self.mb.sgb_border.get_border_buffer()

    def get_composited_frame(self):
        """
        Get the composited frame with SGB border and Game Boy screen.

        Returns:
            array: The composited frame buffer in RGBA format (256x224)
        """
        # Get the game frame - try renderer first, then fall back to LCD
        if hasattr(self.mb, "lcd"):
            if hasattr(self.mb.lcd, "renderer") and hasattr(self.mb.lcd.renderer, "_screenbuffer_raw"):
                game_frame = self.mb.lcd.renderer._screenbuffer_raw
            elif hasattr(self.mb.lcd, "_screenbuffer_raw"):
                game_frame = self.mb.lcd._screenbuffer_raw
            else:
                # Fallback: create empty frame
                from array import array

                game_frame = array("B", [0] * (144 * 160 * 4))
        else:
            # Motherboard doesn't have LCD - create empty frame
            from array import array

            game_frame = array("B", [0] * (144 * 160 * 4))

        return self.mb.sgb_border.get_composited_frame(game_frame)

    def set_joypad_data(self, joypad_index, data):
        """
        Set joypad data for multiplayer support.

        Args:
            joypad_index: Index of joypad (0-3)
            data: Button data for this joypad
        """
        self.mb.sgb.set_joypad_data(joypad_index, data)

    def set_current_joypad(self, joypad_index):
        """
        Set the currently selected joypad.

        Args:
            joypad_index: Index of joypad to select (0-3)
        """
        self.mb.sgb.set_current_joypad(joypad_index)
