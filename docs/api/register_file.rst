Register file
=============

**Technical overview.** The Game Boy CPU has 8-bit registers `A`, `F`, `B`,
`C`, `D`, and `E`, along with the 16-bit register pairs `HL`, `SP`, and `PC`.
The `F` register contains the CPU flags, while `PC` and `SP` track execution
and the stack.

**Using the API.** :class:`PyBoyRegisterFile <pyboy.PyBoyRegisterFile>` is
exposed as :attr:`pyboy.register_file <pyboy.PyBoy.register_file>`. Its
properties read and write the CPU registers, making it useful from a callback
registered with :meth:`pyboy.PyBoy.hook_register`, where execution is paused
at a precise instruction.

.. autoclass:: pyboy.PyBoyRegisterFile
   :members:
   :show-inheritance:
