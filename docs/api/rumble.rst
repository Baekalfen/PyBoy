Rumble
======

**Technical overview.** Some Game Boy Color cartridges, such as the MBC5
rumble cartridge, contain a motor controlled by the cartridge hardware. The
game switches that hardware state as part of its normal cartridge accesses.

**Using the API.** The :class:`Rumble <pyboy.api.rumble.Rumble>` object reports
whether the current cartridge supports rumble and whether the game currently
requests vibration. Read :attr:`supported
<pyboy.api.rumble.Rumble.supported>` and :attr:`enabled
<pyboy.api.rumble.Rumble.enabled>` during the emulation loop and forward the
state to the application or controller that provides physical feedback.

.. automodule:: pyboy.api.rumble
   :members:
   :show-inheritance:
