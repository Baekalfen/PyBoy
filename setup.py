import multiprocessing
import os
import platform
import sys
from multiprocessing import cpu_count

from setuptools import Extension, setup

CYTHON = platform.python_implementation() == "CPython"
ROOT_DIR = "pyboy"

if not CYTHON:
    setup()
    exit(0)

import numpy as np
from Cython.Build import cythonize
from Cython.Compiler import DebugFlags, Errors
from Cython.Distutils import build_ext as _build_ext


def patched_error(position, message):
    if message == "Python object cannot be passed as a varargs parameter":
        # We ignore this error to pass PyObject* to logging
        return
    else:
        #print("Errors.error:", repr(position), repr(message)) ###
        if position is None:
            raise Errors.InternalError(message)
        err = Errors.CompileError(position, message)
        if DebugFlags.debug_exception_on_error:
            raise Exception(err) # debug
        Errors.report_error(err)
        return err


Errors.error = patched_error


class build_ext(_build_ext):
    def initialize_options(self):
        super().initialize_options()
        self.parallel = cpu_count()

        if sys.platform == "win32":
            thread_count = 0 # Disables multiprocessing
        else:
            thread_count = cpu_count()

        # Fixing issue with nthreads in Cython
        if (3,
            8) <= sys.version_info[:2] and sys.platform == "darwin" and multiprocessing.get_start_method() == "spawn":
            multiprocessing.set_start_method("fork", force=True)

        cflags = ["-O3"]
        # NOTE: For performance. Check if other platforms need an equivalent change.
        if sys.platform == "darwin":
            cflags.append("-DCYTHON_INLINE=inline __attribute__ ((__unused__)) __attribute__((always_inline))")

        py_pxd_files = prep_pxd_py_files()
        cythonize_files = map(
            lambda src: Extension(
                src.split(".")[0].replace(os.sep, "."),
                [src],
                extra_compile_args=cflags,
                extra_link_args=["-s", "-w"],
                include_dirs=[np.get_include()],
            ), list(py_pxd_files)
        )
        self.distribution.ext_modules = cythonize(
            [*cythonize_files],
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
                "legacy_implicit_noexcept": True,
            },
        )


def prep_pxd_py_files():
    ignore_py_files = ["__main__.py", "manager_gen.py", "opcodes_gen.py", "conftest.py"]
    # Cython doesn't trigger a recompile on .py files, where only the .pxd file has changed. So we fix this here.
    # We also yield the py_files that have a .pxd file, as we feed these into the cythonize call.
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if os.path.splitext(f)[1] in [".py", ".pyx"] and f not in ignore_py_files:
                yield os.path.join(root, f)
            if os.path.splitext(f)[1] == ".pxd":
                py_file = os.path.join(root, os.path.splitext(f)[0]) + ".py"
                if os.path.isfile(py_file):
                    if os.path.getmtime(os.path.join(root, f)) > os.path.getmtime(py_file):
                        os.utime(py_file)


setup(
    cmdclass={
        "build_ext": build_ext,
    },
    ext_modules=[Extension("", [""])], # Added to trigger a binary wheel
)
