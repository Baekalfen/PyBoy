import os
import sys
from distutils.command.clean import clean as _clean
from distutils.command.clean import log
from distutils.dir_util import remove_tree
from multiprocessing import cpu_count

from setuptools import Extension, find_packages, setup

from Cython.Build import cythonize
from Cython.Distutils import build_ext

ROOT_DIR = "pyboy"


# Cython currently has a bug in its code that results in symbol collision on Windows
def get_export_symbols(self, ext):
    parts = ext.name.split(".")
    initfunc_name = "PyInit_" + parts[-2] if parts[-1] == "__init__" else parts[-1]  # noqa: F841


# Override function in Cython to fix symbol collision
build_ext.get_export_symbols = get_export_symbols


# Add inplace functionality to the clean command
class clean(_clean):
    user_options = _clean.user_options + [("inplace", "i", "remove all output from an inplace build")]
    boolean_options = _clean.boolean_options + ["inplace"]

    def initialize_options(self):
        super().initialize_options()
        self.inplace = None

    def run(self):
        super().run()
        if self.inplace:
            for root, dirs, files in os.walk(ROOT_DIR):
                if "__pycache__" in dirs:
                    log.info(f"Removing: {os.path.join(root, '__pycache__')}")
                    remove_tree(os.path.join(root, "__pycache__"))
                for f in files:
                    if os.path.splitext(f)[1] in (".pyo", ".pyc", ".pyd", ".so", ".c", ".h",
                                                  ".dll", ".lib", ".exp", ".html"):
                        print(f"Removing: {os.path.join(root, f)}")
                        os.remove(os.path.join(root, f))


# Locate the directory with SDL2 headers and library
def locate_sdl2_config():
    print("Searching for SDL2 path")
    if sys.platform == "win32" and any(map(lambda x: "msys" in x, sys.path)):
        print("Detected msys, looking for sdl2-config")
        msys_sh = None
        msys_sdl2_config = None
        for path in os.getenv("PATH").split(";"):
            if not msys_sh and os.path.isfile(os.path.join(path, "sh.exe")):
                msys_sh = f"{path}\\sh.exe"
            if not msys_sdl2_config and os.path.isfile(os.path.join(path, "sdl2-config")):
                msys_sdl2_config = f"{path}\\sdl2-config"
        if msys_sh and msys_sdl2_config:
            print(f"Found sdl2-config at {msys_sdl2_config} and shell at {msys_sh}")
            msys_sdl2_config = msys_sdl2_config.replace("\\", "/")
            msys_mingw_prefix = msys_sdl2_config[:msys_sdl2_config.index('/bin')]
            msys_sdl2_config = f"/{msys_sdl2_config[0].lower()}/{msys_sdl2_config[2:]}"
            return os.popen(f"{msys_sh} -c '{msys_sdl2_config} --prefix={msys_mingw_prefix}"
                            f" --cflags --libs'").read().split()
        else:
            print(f"Could not find shell ({msys_sh}) and sdl2-config ({msys_sdl2_config})")
            return None
    else:
        print("Didn't detect Windows environment, defaulting to Unix-like system.")
        return os.popen("sdl2-config --cflags --libs").read().split()


# Define libs, libdirs, includes and cflags for SDL2
def define_lib_includes_cflags():
    sdl2_config = locate_sdl2_config()
    sdl2_path = os.getenv("PYSDL2_DLL_PATH")
    libs = []
    libdirs = []
    includes = []
    cflags = []
    if sdl2_config is not None:
        for arg in sdl2_config:
            if arg.startswith("-l"):
                libs += [arg[2:]]
            elif arg.startswith("-L"):
                libdirs += [arg[2:]]
            elif arg.startswith("-I"):
                includes += [arg[2:]]
            else:
                cflags += [arg]
        print("SDL2 found using sdl2-config")
    elif sdl2_path:
        sdl2_path = os.path.abspath(sdl2_path[:sdl2_path.index("lib")])
        if not os.path.isdir(sdl2_path):
            print(f"Error locating SDL2: {sdl2_path} is not a directory")
            sys.exit(1)
        else:
            print(f"Found SDL2 at {sdl2_path}")
            libs += ['SDL2']
            libdirs += [os.path.join(sdl2_path, 'lib/x86')]
            includes += [os.path.join(sdl2_path, p) for p in ('include', 'include/SDL2')]
    else:
        print("SDL2 cannot be found through either sdl2-config or PYSDL2_DLL_PATH")
        sys.exit(1)

    return libs, libdirs, includes, cflags


# Cython doesn't trigger a recompile on .py files, where only the .pxd file has changed. So we fix this here.
def touch_changed_py_files():
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if os.path.splitext(f)[1] == ".pxd":
                py_file = os.path.join(root, os.path.splitext(f)[0]) + ".py"
                if os.path.isfile(py_file) and os.path.getmtime(os.path.join(root, f)) > os.path.getmtime(py_file):
                    os.utime(py_file)


# Set up some values for use in setup()
libs, libdirs, includes, cflags = define_lib_includes_cflags()
thread_count = cpu_count() if sys.platform != 'win32' else 0  # 0 disables multiprocessing (windows)
touch_changed_py_files()

with open('../README.md', 'r') as rm:
    long_description = rm.read()


# Cython seems to cythonize these before cleaning, so we only add them, if we aren't cleaning.
if 'clean' not in sys.argv:
    cythonize_files = map(lambda src: Extension(
                src.split('.')[0].replace('/', '.'), [src],
                include_dirs=includes,
                library_dirs=libdirs,
                libraries=libs,
                extra_compile_args=cflags), [
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
                ])
else:
    cythonize_files = []

setup(
    name='PyBoy',
    version='0.1',
    packages=find_packages(),
    author="Mads Ynddal",
    author_email="mads-pyboy@ynddal.dk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Baekalfen/PyBoy",
    classifiers=[
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Emulators",
    ],
    cmdclass={'build_ext': build_ext, 'clean': clean},
    install_requires=[
        "cython",
        "pysdl2",
        "numpy",
        "Pillow",
    ],
    extras_require={
        "all": [
            "pyopengl",
            "pytest-xdist",
            "markdown",
            "pdoc3",
        ],
    },
    zip_safe=False,
    ext_modules=cythonize(
        [*cythonize_files], # This runs even if build_ext isn't invoked...
        nthreads=thread_count,
        annotate=False,
        gdb_debug=False,
        language_level=2,
        compiler_directives={
            "boundscheck": False,
            "cdivision": True,
            "cdivision_warnings": False,
            "infer_types" : True,
            "initializedcheck": False,
            "nonecheck": False,
            "overflowcheck": False,
            # "profile" : True,
            "wraparound": False,
        },
    )
)
