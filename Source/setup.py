# from distutils.core import setup
from Cython.Build import cythonize

# setup(
#   name = 'CPU',
#   ext_modules = cythonize([
#         '__init__.pyx',
#         'flags.pyx',
#         'Interrupts.pyx',
#         'opcodes.pyx',
#         'registers.pyx',
#       ]),
# )


from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy as np

# foo = Extension(name='foo.__init__', sources=['foo/__init__.pyx'])
# bar = Extension(name='foo.bar', sources=['foo/bar.pyx'])

import multiprocessing

thread_count = multiprocessing.cpu_count()
# thread_count = multiprocessing.cpu_count()/2 # Half for Hyper-Threading
# thread_count = 1
print "Thread Count:", thread_count

setup(
    name='PyBoy',
    packages = ["PyBoy"],
    cmdclass={'build_ext':build_ext},
    include_dirs=[".", "PyBoy", "PyBoy/Cartridge", "PyBoy/MB", np.get_include(), "/usr/local/include/SDL2/"], #, "PyBoy/GameWindow",
    ext_modules = cythonize([
            'PyBoy/MathUint8.py',
            'PyBoy/LCD.py',
            'PyBoy/BootROM.py',
            'PyBoy/WindowEvent.py',
            'PyBoy/Cartridge/__init__.py',
            'PyBoy/Cartridge/GenericMBC.py',
            'PyBoy/Cartridge/MBC1.py',
            'PyBoy/Cartridge/MBC2.py',
            'PyBoy/Cartridge/MBC3.py',
            'PyBoy/Cartridge/MBC5.py',
            'PyBoy/Cartridge/RTC.py',
            'PyBoy/RAM.py',
            'PyBoy/Interaction.py',
            # # 'PyBoy/GameWindow/AbstractGameWindow.py',
            'PyBoy/GameWindow/__init__.py',
            'PyBoy/GameWindow/GameWindow_SDL2.py',
            'PyBoy/GameWindow/GameWindow_dummy.py',
            'PyBoy/MB/CPU.py',
            'PyBoy/MB/opcodes.py',
            'PyBoy/MB/Timer.py',
            'PyBoy/MB/MB.py',
            'PyBoy/MB/__init__.py',
            'PyBoy/Global.py',
            'PyBoy/__init__.py',
            'PyBoy/PyBoy.py',
        ],
        include_path=[".", "PyBoy", "PyBoy/Cartridge", "PyBoy/MB", "PyBoy/GameWindow", np.get_include(), "/usr/local/lib/python2.7/site-packages/sdl2/", "/usr/local/include/SDL2/"], #, "PyBoy/GameWindow",
        nthreads=thread_count,
        annotate=True,
        language_level='2',
    )
)
