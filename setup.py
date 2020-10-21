import distutils.cmd
import os
import platform
import shutil
import subprocess
import sys
from distutils.command.clean import clean as _clean
from distutils.command.clean import log
from distutils.dir_util import remove_tree
from multiprocessing import cpu_count
from pathlib import Path

from setuptools import Extension, find_packages, setup
from setuptools.command.test import test

from tests.utils import kirby_rom, supermarioland_rom, tetris_rom

# The requirements.txt file will not be included in the PyPi package
REQUIREMENTS = """\
# Change in setup.py
cython>=0.29.16; platform_python_implementation == 'CPython'
numpy
pillow
pysdl2
"""


def load_requirements(filename):
    if os.path.isfile(filename):
        with open(filename, "w") as f:
            f.write(REQUIREMENTS)
    return [line.split(";")[0].strip() for line in REQUIREMENTS.splitlines()]


requirements = load_requirements("requirements.txt")

MSYS = os.getenv("MSYS")
CYTHON = platform.python_implementation() != "PyPy"

if CYTHON:
    # "Recommended" method of installing Cython: https://github.com/pypa/pip/issues/5761
    from setuptools import dist
    dist.Distribution().fetch_build_eggs(["cython>=0.29.16"])

    from Cython.Build import cythonize
    import Cython.Compiler.Options
    from Cython.Distutils import build_ext
else:
    try:
        for r in requirements:
            if "cython" in r:
                break
        else:
            r = None
        requirements.remove(r)
    except ValueError:
        pass

    class build_ext(distutils.cmd.Command):
        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            pass


ROOT_DIR = "pyboy"

codecov = "--codecov-trace" in sys.argv

if codecov:
    sys.argv.pop(sys.argv.index("--codecov-trace"))
    directive_defaults = Cython.Compiler.Options.get_directive_defaults()
    directive_defaults["linetrace"] = True
    directive_defaults["binding"] = True


class PyTest(test):
    def finalize_options(self):
        super().finalize_options()
        self.test_suite = True
        self.test_args = []

    def run_tests(self):
        if not os.environ.get("TEST_NO_EXAMPLES"):
            script_path = os.path.dirname(os.path.realpath(__file__))
            base = Path(f"{script_path}/examples/")

            for gamewrapper, rom in [
                ("gamewrapper_tetris.py", tetris_rom),
                ("gamewrapper_mario.py", supermarioland_rom),
                ("gamewrapper_kirby.py", kirby_rom),
            ]:
                if rom is None:
                    continue

                return_code = subprocess.Popen([sys.executable,
                                                str(base / gamewrapper),
                                                str(Path(rom)), "--quiet"]).wait()
                if return_code != 0:
                    sys.exit(return_code)

        import pytest
        args = ["tests/", f"-n{cpu_count()}", "-v", "--dist=loadfile"]
        # args = ["tests/", "-v", "-x"] # No multithreading, fail fast
        if codecov: # TODO: There's probably a more correct way to read the argv flags
            args += ["--cov=./"]
        sys.exit(pytest.main(args))


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
            for p in ("PyBoy.egg-info", "build", "dist"):
                if os.path.isdir(p):
                    shutil.rmtree(p)

            for root, dirs, files in os.walk(ROOT_DIR):
                if "__pycache__" in dirs:
                    log.info(f"removing: {os.path.join(root, '__pycache__')}")
                    remove_tree(os.path.join(root, "__pycache__"))
                for f in files:
                    if os.path.splitext(f)[1] in (
                        ".pyo", ".pyc", ".pyd", ".so", ".c", ".h", ".dll", ".lib", ".exp", ".html"
                    ):
                        print(f"removing: {os.path.join(root, f)}")
                        os.remove(os.path.join(root, f))


# Locate the directory with SDL2 headers and library
def locate_sdl2_config():
    print("Searching for SDL2 installation")
    if sys.platform == "win32" and "GCC" in platform.python_compiler():
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
            msys_mingw_prefix = msys_sdl2_config[:msys_sdl2_config.index("/bin")]
            msys_sdl2_config = f"/{msys_sdl2_config[0].lower()}/{msys_sdl2_config[2:]}"
            return os.popen(f"{msys_sh} -c '{msys_sdl2_config} --prefix={msys_mingw_prefix}"
                            f" --cflags --libs'").read().split()
        else:
            print(f"Could not find shell ({msys_sh}) and sdl2-config ({msys_sdl2_config})")
            return None
    elif sys.platform == "win32" and "MSC" in platform.python_compiler():
        return [] # Defaults to env var PYSDL2_DLL_PATH
    elif sys.platform in ["darwin", "linux"]:
        print("Didn't detect msys2 environment, trying sdl2-config assuming Unix environment")
        return os.popen("sdl2-config --cflags --libs").read().split()
    else:
        print(f"Unsupported OS type: {sys.platform}")
        sys.exit(121)


# Define libs, libdirs, includes and cflags for SDL2
def define_lib_includes_cflags():
    sdl2_config = locate_sdl2_config()
    sdl2_path = os.getenv("PYSDL2_DLL_PATH")
    libs = []
    libdirs = []
    includes = []
    cflags = []
    if sdl2_config != []:
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
        print("No sdl2-config found, using PYSDL2_DLL_PATH variable")
        sdl2_lib_arch = "x86" if "x86" in sdl2_path else "x64" if "x64" in sdl2_path else ""
        sdl2_path = os.path.abspath(sdl2_path[:sdl2_path.index("lib")])
        if not os.path.isdir(sdl2_path):
            print(f"Error locating SDL2: {sdl2_path} is not a directory")
            sys.exit(122)
        else:
            print(f"Found SDL2 at {sdl2_path}")
            libs += ["SDL2"]
            libdirs += [os.path.join(sdl2_path, "lib", sdl2_lib_arch)]
            includes += [os.path.join(sdl2_path, "include", p) for p in ("", "SDL2")]
    else:
        print("SDL2 cannot be found through neither sdl2-config nor PYSDL2_DLL_PATH")
        sys.exit(123)

    return libs, libdirs, includes, cflags


def prep_pxd_py_files():
    ignore_py_files = ["__main__.py", "manager_gen.py", "opcodes_gen.py"]
    # Cython doesn't trigger a recompile on .py files, where only the .pxd file has changed. So we fix this here.
    # We also yield the py_files that have a .pxd file, as we feed these into the cythonize call.
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if os.path.splitext(f)[1] == ".py" and f not in ignore_py_files:
                yield os.path.join(root, f)
            if os.path.splitext(f)[1] == ".pxd":
                py_file = os.path.join(root, os.path.splitext(f)[0]) + ".py"
                if os.path.isfile(py_file):
                    if os.path.getmtime(os.path.join(root, f)) > os.path.getmtime(py_file):
                        os.utime(py_file)


# Cython seems to cythonize these before cleaning, so we only add them, if we aren't cleaning.
ext_modules = None
if CYTHON and "clean" not in sys.argv:
    if sys.platform == "win32":
        # Cython currently has a bug in its code that results in symbol collision on Windows
        def get_export_symbols(self, ext):
            parts = ext.name.split(".")
            initfunc_name = "PyInit_" + parts[-2] if parts[-1] == "__init__" else parts[-1] # noqa: F841

        # Override function in Cython to fix symbol collision
        build_ext.get_export_symbols = get_export_symbols
        thread_count = 0 # Disables multiprocessing (windows)
    elif platform.python_version().startswith("3.8"):
        # Causes infinite recursion
        thread_count = 0
    else:
        thread_count = cpu_count()

    # Set up some values for use in setup()
    libs, libdirs, includes, cflags = define_lib_includes_cflags()

    py_pxd_files = prep_pxd_py_files()
    cythonize_files = map(
        lambda src: Extension(
            src.split(".")[0].replace(os.sep, "."), [src],
            include_dirs=includes,
            library_dirs=libdirs,
            libraries=libs,
            extra_compile_args=cflags
        ), list(py_pxd_files)
    )
    ext_modules = cythonize(
        [*cythonize_files], # This runs even if build_ext isn't invoked...
        nthreads=thread_count,
        annotate=False,
        gdb_debug=False,
        language_level=3,
        compiler_directives={
            "boundscheck": False,
            "cdivision": True,
            "cdivision_warnings": False,
            "infer_types": True,
            "initializedcheck": False,
            "nonecheck": False,
            "overflowcheck": False,
            # "profile" : True,
            "wraparound": False,
        },
    )

try:
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    print("README.md not found")
    long_description = ""

setup(
    name="pyboy",
    version="1.3.0",
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
    entry_points={
        "console_scripts": ["pyboy = pyboy.__main__:main", ],
    },
    cmdclass={
        "build_ext": build_ext,
        "clean": clean,
        "test": PyTest
    },
    install_requires=requirements,
    tests_require=[
        "pytest>=6.0.0",
        "pytest-xdist",
        "pyopengl",
        "gym" if CYTHON and not MSYS else "",
    ],
    extras_require={
        "all": [
            "pyopengl",
            "markdown",
            "pdoc3",
            "gym" if CYTHON and not MSYS else "",
        ],
    },
    zip_safe=(not CYTHON), # Cython doesn't support it
    ext_modules=ext_modules,
    python_requires=">=3.6",
    package_data={"": ["*.pyx", "*.pxd", "*.c", "*.h", "bootrom.bin"]},
)
