Memory view
===========

**Technical overview.** The Game Boy exposes a 16-bit address space, but parts
of that space are shared with banked ROM, cartridge RAM, video RAM, and
working RAM. Hardware registers also live in the address space and can have
side effects when read or written.

.. autoclass:: pyboy.PyBoyMemoryView
   :members:
   :show-inheritance:
