#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import platform
from threading import Thread

import pytest

from pyboy import PyBoy

is_pypy = platform.python_implementation() == "PyPy"


@pytest.mark.benchmark(group="nogil")
def test_threads_baseline(benchmark, default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    benchmark(pyboy.tick, 2000, False)


@pytest.mark.skipif(is_pypy, reason="No-GIL is not relevant for PyPy")
@pytest.mark.benchmark(group="nogil")
@pytest.mark.parametrize("count", [1, 2, 4])
def test_threads_nogil(benchmark, count, default_rom):
    # Threaded run with no GIL. Should result in roughly same time.
    def thread_run():
        pyboy = PyBoy(default_rom, window="null")
        pyboy.set_emulation_speed(0)
        pyboy.tick(2000, False)

    def bench():
        threads = [Thread(target=thread_run) for _ in range(count)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

    benchmark(bench)
