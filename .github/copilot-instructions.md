Remember to run 'make clean; make' if you change the code, as the code is compiled with Cython.
Make type-annotations only in .pxd files. Keep the .py files free of Cython dependencies.
Prefer array.array and memoryview over NumPy when possible. NumPy can be used for user-facing API code.
Watch out for the hotpaths in CPU.tick, Motherboard.tick, Motherboard.getitem and Motherboard.setitem
The tests are run with 'python3 -m pytest tests/ -v' after compilation. There are also tests in 'python3 -m pytest pyboy/ -v' but these require PyBoy to *not* be compiled. Use these sparingly, as they take much longer time, and often don't proof much. But can be used as a final test.
Whenever the given task completes, rerun the entire testsuite. Both tests/ and pyboy/ tests.
The SameBoy repo is an excellent source of a really precise Game Boy emulator https://github.com/LIJI32/SameBoy
The Gambatte repo can also be a good source https://github.com/gb-archive/gambatte/tree/master
The Pan Docs are really good for a detailed source of information as well, although not as thorough https://gbdev.io/pandocs/
Use the internet to find disassemblies or the source code of ROMs when applicable.