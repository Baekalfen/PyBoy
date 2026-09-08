#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
Rumble Pack API for accessing rumble state of games like Pokémon Pinball.

The rumble pack was an accessory for Game Boy Color that provided vibration feedback.
It was controlled through MBC5 cartridge to the rumble motor.

"""


class Rumble:
    """
    Provides access to the current rumble pack state.

    For frame-by-frame access, read the state properties each frame during the
    emulation loop and store the data as needed.

    Example:
    ```python
    >>> rumble_history = []
    >>> for _ in range(10):
    ...     pyboy.tick()
    ...     rumble_history.append(pyboy.rumble.enabled)
    True...

    ```

    """

    def __init__(self, mb):
        self.mb = mb

    @property
    def enabled(self):
        """
        Current rumble state.

        Returns
        -------
        bool: True if the rumble motor should be vibrating, False otherwise.
        """
        return bool(self.mb.cartridge.rumble_supported and self.mb.cartridge.rumble_enabled)

    @property
    def supported(self):
        """
        Whether the current cartridge supports rumble functionality.

        Returns
        -------
        bool: True if the cartridge supports rumble, False otherwise.
        """
        return bool(self.mb.cartridge.rumble_supported)
