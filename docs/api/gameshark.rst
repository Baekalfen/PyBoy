GameShark
=========

**Technical overview.** A GameShark code encodes a memory write as a type,
value, and address in an eight-digit hexadecimal string. Applying a code
changes the emulated memory at the point where the cheat is processed, which
allows game state such as scores or inventory values to be altered.

**Using the API.** The :class:`GameShark <pyboy.api.gameshark.GameShark>`
object is available from :class:`PyBoy <pyboy.PyBoy>` and accepts codes
through :meth:`add <pyboy.api.gameshark.GameShark.add>`. It reapplies active
codes while emulation runs, and :meth:`remove
<pyboy.api.gameshark.GameShark.remove>` or :meth:`clear_all
<pyboy.api.gameshark.GameShark.clear_all>` can restore the values that were
present before the cheats were added.

.. automodule:: pyboy.api.gameshark
   :no-members:

.. autoclass:: pyboy.api.gameshark.GameShark
   :members:
   :special-members: __init__
   :show-inheritance:
