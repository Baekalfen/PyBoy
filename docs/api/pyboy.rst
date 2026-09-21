PyBoy
=====

**Technical overview.** PyBoy emulates the Game Boy and Game Boy Color system,
including the CPU, memory map, graphics, audio, cartridge hardware, and input
devices. The main object coordinates these components while the game advances
one frame at a time.

**Using the API.** Create a :class:`PyBoy <pyboy.PyBoy>` instance with a ROM,
call :meth:`tick <pyboy.PyBoy.tick>` to advance emulation, and use its
properties and methods to send input or inspect hardware state. Start with the
small example below and add more control only when you need it.

Minimal example
---------------

This runs a game for a few seconds and then stops the emulator:

.. code-block:: python

   from pyboy import PyBoy

   pyboy = PyBoy("game.gb")
   pyboy.tick(60 * 5)
   pyboy.stop()

The :meth:`tick <pyboy.PyBoy.tick>` call advances the game by 300 frames. Use
a loop when you want to inspect or control the game as it runs:

.. code-block:: python

   from pyboy import PyBoy

   pyboy = PyBoy("game.gb", window="null")
   pyboy.set_emulation_speed(0)

   for _ in range(60):
       pyboy.tick()

   print(pyboy.cartridge_title)
   pyboy.stop()

Inspecting and controlling a game
---------------------------------

The controller exposes higher-level helpers for input and lower-level views
for the emulated hardware. This example presses a button, reads a memory
address, and captures the current screen:

.. code-block:: python

   from pyboy import PyBoy

   pyboy = PyBoy("game.gb", window="null")
   pyboy.set_emulation_speed(0)

   pyboy.button_press("a")
   pyboy.tick(30)
   pyboy.button_release("a")

   print("Value at C000:", pyboy.memory[0xC000])
   pyboy.screen.image.save("frame.png")
   pyboy.stop()

For direct memory access, see the :doc:`memory view <memory_view>` page. For
CPU registers, see the :doc:`register file <register_file>` page. The
remaining sections document the full :class:`PyBoy <pyboy.PyBoy>` controller
API.

.. autoclass:: pyboy.PyBoy
   :members:
   :show-inheritance:
