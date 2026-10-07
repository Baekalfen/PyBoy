Super Game Boy
==============

**Technical overview.** The Super Game Boy is a Game Boy cartridge for the
SNES. Games that support it send commands through the joypad port to request
a screen border, custom palettes, and multiplayer joypads. The commands
transfer border tiles, tile map, and palette data as pixels drawn on the
LCD, which the emulator captures a few frames later.

**Using the API.** The :class:`SGB <pyboy.api.sgb.SGB>` object reports whether
the loaded cartridge supports Super Game Boy features and whether they are
enabled. Pass ``sgb_border=True`` to the
:class:`PyBoy <pyboy.PyBoy>` constructor to enable SGB processing and border
rendering in the SDL2 and GLFW windows.

.. automodule:: pyboy.api.sgb
   :members:
   :show-inheritance:
