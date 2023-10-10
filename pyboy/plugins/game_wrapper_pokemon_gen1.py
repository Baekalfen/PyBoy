#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperPokemonGen1.cartridge_title": False,
    "GameWrapperPokemonGen1.post_tick": False,
}

import logging

from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

logger = logging.getLogger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue, and provides basic access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = None

    def __init__(self, *args, **kwargs):
        self.shape = (20, 18)
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)
        self.sprite_offset = 0x1000

    def enabled(self):
        return self.pyboy_argv.get("game_wrapper") and ((self.pyboy.cartridge_title() == "POKEMON RED") or
                                                        (self.pyboy.cartridge_title() == "POKEMON BLUE"))

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        scanline_parameters = self.pyboy.botsupport_manager().screen().tilemap_position_list()
        WX = scanline_parameters[0][2]
        WY = scanline_parameters[0][3]
        self.use_background(WY != 0)

    def __repr__(self):
        adjust = 4
        # yapf: disable
        return (
            f"Pokemon Gen 1:\n" +
            "Sprites on screen:\n" +
            "\n".join([str(s) for s in self._sprites_on_screen()]) +
            "\n" +
            "Tiles on screen:\n" +
            " "*5 + "".join([f"{i: <4}" for i in range(10)]) + "\n" +
            "_"*(adjust*20+4) +
            "\n" +
            "\n".join(
                [
                    f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                    for i, line in enumerate(self.game_area())
                ]
            )
        )
        # yapf: enable
