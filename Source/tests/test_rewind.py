import sys

sys.path.append(".") # isort:skip
from pyboy.rewind import FixedAllocBuffers # isort:skip

a = FixedAllocBuffers()


def write_bytes(a, values):
    for v in values:
        a.write(v % 0xFF)


def test_buffer():
    A = [x % 0xFF for x in range(0, 10)]
    B = [x % 0xFF for x in range(10, 23)]
    C = [x % 0xFF for x in range(5, 14)]
    D = [x % 0xFF for x in range(3, 39)]

    for E in [A, B, C, D]:
        write_bytes(a, E)
        a.new()

    for E in [D, C, B, A]:
        a.seek_frame(-1)
        tests = [(x, a.read()) for x in E]
        assert all(list(map(lambda x: x[0] == x[1], tests)))


if __name__ == "__main__":
    test_buffer()
