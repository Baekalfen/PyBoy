from setuptools import find_packages, setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext

from multiprocessing import cpu_count

with open('../README.md', 'r') as rm:
	    long_description = rm.read()

thread_count = cpu_count()
print("Thread Count:", thread_count)

setup(
    name='PyBoy',
    version='0.1',
    # packages = ["PyBoy"],
    packages=find_packages(),
    author="Mads Ynddal",
    author_email="mads-pyboy@ynddal.dk",
    long_description=long_description,
    content_type="text/markdown",
    url="https://github.com/Baekalfen/PyBoy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Topic :: System :: Emulators",
    ],
    cmdclass={'build_ext':build_ext},
    install_requires=[
        "cython",
        "pysdl2",
        "numpy",
        ],
    extras_require={
        "all" : [
            "pyopengl",
            "imageio",
            ],
        },
    include_dirs=[".", "PyBoy", "PyBoy/Cartridge", "PyBoy/Window", "PyBoy/MB"],
    ext_modules = cythonize([
            'PyBoy/LCD.py',
            'PyBoy/BootROM.py',
            'PyBoy/WindowEvent.py',
            'PyBoy/Cartridge/__init__.py',
            # 'PyBoy/Cartridge/Cartridge.py',
            'PyBoy/Cartridge/GenericMBC.py',
            'PyBoy/Cartridge/MBC1.py',
            'PyBoy/Cartridge/MBC2.py',
            'PyBoy/Cartridge/MBC3.py',
            'PyBoy/Cartridge/MBC5.py',
            'PyBoy/Cartridge/RTC.py',
            'PyBoy/RAM.py',
            'PyBoy/Interaction.py',
            # # 'PyBoy/Window/AbstractWindow.py',
            'PyBoy/Window/__init__.py',
            'PyBoy/Window/GenericWindow.py',
            'PyBoy/Window/Window.py',
            'PyBoy/Window/Window_SDL2.py',
            'PyBoy/Window/Window_OpenGL.py',
            'PyBoy/Window/Window_Scanline.py',
            'PyBoy/Window/Window_dummy.py',
            'PyBoy/MB/CPU.py',
            'PyBoy/MB/opcodes.py',
            'PyBoy/MB/Timer.py',
            'PyBoy/MB/MB.py',
            'PyBoy/MB/__init__.py',
            'PyBoy/__init__.py',
            'PyBoy/PyBoy.py',
            'PyBoy/ScreenRecorder.py',
            'PyBoy/BotSupport/Sprite.py',
            'PyBoy/BotSupport/TileView.py',
        ],
        include_path=[".", "PyBoy", "PyBoy/Cartridge", "PyBoy/MB", "PyBoy/Window"],
        nthreads=thread_count,
        annotate=False,
        language_level=2,
        compiler_directives={
            "cdivision" : True,
            "cdivision_warnings" : False,
            "boundscheck" : False,
            "wraparound" : False,
            "initializedcheck" : False,
            "nonecheck" : False,
            "overflowcheck" : False,
            # # "profile" : True, # For profiling
            # "infer_types" : True,
        },
    )
)

# https://cython.readthedocs.io/en/stable/src/userguide/source_files_and_compilation.html#compiler-options
# TODO?
# Cython.Compiler.Options.convert_range = True
# This will convert statements of the form for i in range(...) to for i from ... when i is a C integer type, and the direction (i.e. sign of step) can be determined. WARNING: This may change the semantics if the range causes assignment to i to overflow. Specifically, if this option is set, an error will be raised before the loop is entered, whereas without this option the loop will execute until an overflowing value is encountered
