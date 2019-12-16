from multiprocessing import cpu_count
from sys import platform

from setuptools import find_packages, setup

from Cython.Build import cythonize
from Cython.Distutils import build_ext


# Cython currently has a bug in its code that results in symbol collision on Windows
def get_export_symbols(self, ext):
    parts = ext.name.split(".")
    initfunc_name = "PyInit_" + parts[-2] if parts[-1] == "__init__" else parts[-1]  # noqa: F841


# Override function in Cython to fix symbol collision
build_ext.get_export_symbols = get_export_symbols

with open('../README.md', 'r') as rm:
    long_description = rm.read()

# Get number of threads to cythonize with. A value of 0 disables multiprocessing.
thread_count = cpu_count() if platform != 'win32' else 0

module_dirs = [".", "pyboy", "pyboy/core", "pyboy/core/cartridge", "pyboy/window", "pyboy/botsupport"]


setup(
    name='PyBoy',
    version='0.1',
    packages=find_packages(),
    author="Mads Ynddal",
    author_email="mads-pyboy@ynddal.dk",
    long_description=long_description,
    url="https://github.com/Baekalfen/PyBoy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Topic :: System :: Emulators",
    ],
    cmdclass={'build_ext': build_ext},
    install_requires=[
        "cython",
        "pysdl2",
    ],
    extras_require={
        "all": [
            "numpy",
            "pyopengl",
            "Pillow",
            "pytest-xdist",
            "markdown",
            "pdoc3",
        ],
    },
    include_dirs=module_dirs,
    zip_safe=False,
    ext_modules=cythonize([
        'pyboy/__init__.py',
        'pyboy/botsupport/sprite.py',
        'pyboy/botsupport/spritetracker.py',
        'pyboy/botsupport/tile.py',
        'pyboy/botsupport/tilemap.py',
        'pyboy/core/__init__.py',
        'pyboy/core/bootrom.py',
        'pyboy/core/cartridge/__init__.py',
        'pyboy/core/cartridge/base_mbc.py',
        'pyboy/core/cartridge/cartridge.py',
        'pyboy/core/cartridge/mbc1.py',
        'pyboy/core/cartridge/mbc2.py',
        'pyboy/core/cartridge/mbc3.py',
        'pyboy/core/cartridge/mbc5.py',
        'pyboy/core/cartridge/rtc.py',
        'pyboy/core/cpu.py',
        'pyboy/core/interaction.py',
        'pyboy/core/lcd.py',
        'pyboy/core/mb.py',
        'pyboy/core/opcodes.py',
        'pyboy/core/ram.py',
        'pyboy/core/timer.py',
        'pyboy/logger.py',
        'pyboy/pyboy.py',
        'pyboy/rewind.py',
        'pyboy/screenrecorder.py',
        'pyboy/window/__init__.py',
        'pyboy/window/base_window.py',
        'pyboy/window/debug_window.py',
        'pyboy/window/window.py',
        'pyboy/window/window_dummy.py',
        'pyboy/window/window_headless.py',
        'pyboy/window/window_opengl.py',
        'pyboy/window/window_scanline.py',
        'pyboy/window/window_sdl2.py',
        'pyboy/windowevent.py',
    ],
        include_path=module_dirs,
        nthreads=thread_count,
        annotate=True,
        gdb_debug=False,
        language_level=2,
        compiler_directives={
            "cdivision": True,
            "cdivision_warnings": False,
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "nonecheck": False,
            "overflowcheck": False,
            # "profile" : True,
            "infer_types" : True,
        },
    )
)


# https://cython.readthedocs.io/en/stable/src/userguide/source_files_and_compilation.html#compiler-options
# TODO?
# Cython.Compiler.Options.convert_range = True
# This will convert statements of the form for i in range(...) to for
# i from ... when i is a C integer type, and the direction (i.e. sign
# of step) can be determined. WARNING: This may change the semantics
# if the range causes assignment to i to overflow. Specifically, if
# this option is set, an error will be raised before the loop is
# entered, whereas without this option the loop will execute until an
# overflowing value is encountered
