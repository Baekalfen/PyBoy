import distutils.cmd
import multiprocessing
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

# The requirements.txt file will not be included in the PyPi package
REQUIREMENTS = """\
# Change in setup.py
cython>=0.29.16; platform_python_implementation == 'CPython'
numpy
pysdl2
pysdl2-dll
"""


def load_requirements(filename):
    if os.path.isfile(filename):
        with open(filename, "w") as f:
            f.write(REQUIREMENTS)
    return [line.strip() for line in REQUIREMENTS.splitlines()]


requirements = load_requirements("requirements.txt")

CYTHON = platform.python_implementation() == "CPython"

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
            if r.startswith("cython"):
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


DEBUG = os.getenv("DEBUG")
with open("pyboy/core/debug.pxi", "w") as f:
    f.writelines([
        "#\n",
        "# License: See LICENSE.md file\n",
        "# GitHub: https://github.com/Baekalfen/PyBoy\n",
        "#\n",
        f"DEF DEBUG={int(bool(DEBUG))}\n",
    ])

ROOT_DIR = "pyboy"

codecov = "--codecov-trace" in sys.argv

if codecov:
    sys.argv.pop(sys.argv.index("--codecov-trace"))
    directive_defaults = Cython.Compiler.Options.get_directive_defaults()
    directive_defaults["linetrace"] = True
    directive_defaults["binding"] = True


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


# Define libs, libdirs, includes and cflags for SDL2
def define_lib_includes_cflags():
    libs = []
    libdirs = []
    includes = []
    cflags = [
        "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX11.1.sdk/usr/include"
    ] if sys.platform == "darwin" else []

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
    else:
        thread_count = cpu_count()

    # Fixing issue with nthreads in Cython
    if (3, 8) <= sys.version_info[:2] and sys.platform == "darwin" and multiprocessing.get_start_method() == "spawn":
        multiprocessing.set_start_method("fork", force=True)

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
        long_description = f.read().replace("README/", "https://github.com/Baekalfen/PyBoy/raw/master/README/")
except FileNotFoundError:
    print("README.md not found")
    long_description = ""

setup(
    name="pyboy",
    version="v1.5.5",
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
    },
    install_requires=requirements,
    extras_require={
        "all": [
            "pyopengl",
            "markdown",
            "pdoc3",
            "gym" if CYTHON else "",
        ],
    },
    zip_safe=(not CYTHON), # Cython doesn't support it
    ext_modules=ext_modules,
    python_requires=">=3.8",
    package_data={"": ["*.pxi", "*.pyx", "*.pxd", "*.c", "*.h", "bootrom*.bin", "font.txt"]},
)
