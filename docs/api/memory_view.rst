Memory view
===========

**Technical overview.** The Game Boy exposes a 16-bit address space, but parts
of that space are shared with banked ROM, cartridge RAM, video RAM, and
working RAM. Hardware registers also live in the address space and can have
side effects when read or written.

**Using the API.** :class:`PyBoyMemoryView <pyboy.PyBoyMemoryView>` is the
object behind :attr:`pyboy.memory <pyboy.PyBoy.memory>`. Index it with an
address or a slice to read and write bytes, and provide a bank together with
the address when a specific ROM, RAM, or video-memory bank is needed. ROM
overrides and the special boot-ROM bank are supported as separate forms of
access.

.. autoclass:: pyboy.PyBoyMemoryView
   :members:
   :show-inheritance:
