Tile map
========

**Technical overview.** The background and window each use a 32 by 32 map of
tile identifiers stored in video RAM. The LCD controller selects the map and
the tile-data addressing mode, so an identifier can refer to different pixel
data depending on the current hardware configuration.

**Using the API.** :class:`TileMap <pyboy.api.tilemap.TileMap>` is exposed
through :attr:`pyboy.tilemap_background <pyboy.PyBoy.tilemap_background>` and
:attr:`pyboy.tilemap_window <pyboy.PyBoy.tilemap_window>`. Index it with
coordinates or slices to read identifiers, search for identifiers across the
map, or enable tile objects when the corresponding
:class:`Tile <pyboy.api.tile.Tile>` data is needed.

.. automodule:: pyboy.api.tilemap
   :no-members:

.. autoclass:: pyboy.api.tilemap.TileMap
   :members:
   :show-inheritance:
