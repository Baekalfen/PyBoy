Remember to run 'make clean; make' if you change the code, as the code is compiled with Cython.
Make type-annotations only in .pxd files. Keep the .py files free of Cython dependencies.
Prefer array.array and memoryview over NumPy when possible. NumPy can be used for user-facing API code.
Watch out for the hotpaths in CPU.tick, Motherboard.tick, Motherboard.getitem and Motherboard.setitem
The tests are run with 'python3 -m pytest tests/ pyboy/ docs/ -v' after compilation.
Always run tests with TEST_VERBOSE_IMAGES=0 when run in the background and with TEST_NO_UI=1 when not specifically UI related. Always add a timeout of 2-5 minutes to the tests, as they can hang during development.
Whenever the given task completes, rerun the entire testsuite.
The SameBoy repo is an excellent source of a really precise Game Boy emulator https://github.com/LIJI32/SameBoy
The Gambatte repo can also be a good source https://github.com/gb-archive/gambatte/tree/master
The Pan Docs are really good for a detailed source of information as well, although not as thorough https://gbdev.io/pandocs/
Additional resources can also be found here: https://gbdev.io/resources.html
Use the internet to find disassemblies or the source code of ROMs when applicable.
Any use of the word "simulation" is banned. This is **emulation**.