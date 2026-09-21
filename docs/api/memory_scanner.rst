Memory scanner
==============

**Technical overview.** Game state is stored as changing byte values in the
Game Boy address space. A value may occupy multiple bytes, use a particular
byte order, or be encoded as binary-coded decimal (BCD), so finding it often
requires comparing memory across multiple frames.

**Using the API.** :class:`MemoryScanner
<pyboy.api.memory_scanner.MemoryScanner>` searches an address range with a
standard comparison, then keeps the matching addresses for
:meth:`rescan_memory <pyboy.api.memory_scanner.MemoryScanner.rescan_memory>`
to filter using changes between scans. The comparison and value-type enums
select whether a scan looks for exact, relational, integer, or BCD values.

.. automodule:: pyboy.api.memory_scanner
   :members:
   :show-inheritance:
