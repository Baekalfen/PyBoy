#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from threading import Thread

import pytest

from pyboy import PyBoy
from pyboy.utils import cython_compiled


@pytest.mark.benchmark(group="nogil")
def test_threads_baseline(benchmark, default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    benchmark(pyboy.tick, 2000, False)


@pytest.mark.skipif(not cython_compiled, reason="No-GIL is only relevant for Cython")
@pytest.mark.benchmark(group="nogil")
@pytest.mark.parametrize("count", [1, 2, 4])
def test_threads_nogil(benchmark, count, default_rom):
    # Threaded run with no GIL. Should result in roughly same time.
    def thread_run():
        pyboy = PyBoy(default_rom, window="null")
        pyboy.set_emulation_speed(0)
        pyboy.tick(2000, False, False)

    def bench():
        threads = [Thread(target=thread_run) for _ in range(count)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

    benchmark(bench)
