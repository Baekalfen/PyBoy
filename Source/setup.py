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
    # packages = ["pyboy"],
    packages=find_packages(),
    author="Mads Ynddal",
    author_email="mads-pyboy@ynddal.dk",
    long_description=long_description,
    content_type="text/markdown",
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
            "pyopengl",
            "numpy",
            "Pillow",
        ],
    },
    include_dirs=[".", "pyboy", "pyboy/cartridge", "pyboy/window", "pyboy/mb", "pyboy/debug"],
    zip_safe=False,
    ext_modules=cythonize([
        'pyboy/logger.py',
        'pyboy/lcd.py',
        'pyboy/bootrom.py',
        'pyboy/windowevent.py',
        'pyboy/cartridge/__init__.py',
        # 'pyboy/cartridge/cartridge.py',
        'pyboy/cartridge/base_mbc.py',
        'pyboy/cartridge/mbc1.py',
        'pyboy/cartridge/mbc2.py',
        'pyboy/cartridge/mbc3.py',
        'pyboy/cartridge/mbc5.py',
        'pyboy/cartridge/rtc.py',
        'pyboy/ram.py',
        'pyboy/interaction.py',
        'pyboy/window/__init__.py',
        'pyboy/window/base_window.py',
        'pyboy/window/window_sdl2.py',
        'pyboy/window/debug_window.py',
        'pyboy/window/window_opengl.py',
        'pyboy/window/window_scanline.py',
        'pyboy/window/window_dummy.py',
        'pyboy/window/window_headless.py',
        'pyboy/window/window.py',
        'pyboy/mb/cpu.py',
        'pyboy/mb/opcodes.py',
        'pyboy/mb/timer.py',
        'pyboy/mb/mb.py',
        'pyboy/mb/__init__.py',
        'pyboy/__init__.py',
        'pyboy/pyboy.py',
        'pyboy/screenrecorder.py',
        'pyboy/botsupport/sprite.py',
        'pyboy/botsupport/tilemap.py',
        ],
        include_path=[".", "pyboy", "pyboy/cartridge", "pyboy/mb", "pyboy/window"],
        nthreads=thread_count,
        annotate=False,
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
