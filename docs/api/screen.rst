Screen
======

**Technical overview.** The Game Boy LCD renders a 160 by 144 pixel image.
PyBoy keeps the current frame in a 32-bit RGBA buffer, which is updated as
emulation advances.

**Using the API.** :class:`Screen <pyboy.api.screen.Screen>` exposes the
current frame as a Pillow image, a NumPy array, or the raw buffer, together
with its dimensions and format. The image and array reference live data, so
copy them when a frame must be kept after the next call to
:meth:`tick <pyboy.PyBoy.tick>`.

.. automodule:: pyboy.api.screen
   :members:
   :show-inheritance:
