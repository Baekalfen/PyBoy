Tile
====

**Technical overview.** Tiles are the Game Boy's basic graphics units: each
tile is an 8 by 8 pixel pattern stored as 16 bytes in video RAM, with two bits
per pixel selecting a palette entry. The original Game Boy provides 384 tile
patterns, while Game Boy Color adds a second video-memory bank.

**Using the API.** :class:`Tile <pyboy.api.tile.Tile>` identifies a tile and
its current video-memory location, then exposes the pixels as a Pillow image
or a NumPy array. Tile objects are returned by :meth:`PyBoy.get_tile
<pyboy.PyBoy.get_tile>`, :class:`Sprite <pyboy.api.sprite.Sprite>`, and
:class:`TileMap <pyboy.api.tilemap.TileMap>`; their image data is read from
emulated memory and can change after each :meth:`tick <pyboy.PyBoy.tick>`.

.. automodule:: pyboy.api.tile
   :no-members:

.. autoclass:: pyboy.api.tile.Tile
   :members:
   :show-inheritance:
