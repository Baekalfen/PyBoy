Sprite
======

**Technical overview.** The Game Boy stores up to 40 sprite entries in OAM.
Each entry describes a screen position, a tile, and display attributes such as
flipping, palette, and priority. Sprites can be 8 by 8 or 8 by 16 pixels and
can move independently of the background tile grid.

**Using the API.** :class:`Sprite <pyboy.api.sprite.Sprite>` decodes one OAM
entry into coordinates, attributes, visibility, and its associated
:class:`Tile <pyboy.api.tile.Tile>` objects. Obtain sprites through the
:class:`PyBoy <pyboy.PyBoy>` helpers, then inspect their fields after each
:meth:`tick <pyboy.PyBoy.tick>` because games rewrite OAM frequently.

.. automodule:: pyboy.api.sprite
   :no-members:

.. autoclass:: pyboy.api.sprite.Sprite
   :members:
   :special-members: __init__
   :show-inheritance:
