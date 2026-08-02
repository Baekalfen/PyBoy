#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json
import pytest

from pyboy import PyBoy

OVERWRITE_JSON = False

rtc3test_json = "tests/test_results/rtc3test.json"

CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz. "
SPECIAL_CHARACTERS = {
    0xC0: ">",
    0xC1: "*",
    0xC2: ":",
    0xC3: "/",
    0xC4: "-",
    0xFF: " ",
}


def rtc3test_result(pyboy):
    lines = []
    for y in range(18):
        line = ""
        for x in range(20):
            tile = pyboy.tilemap_background[x, y]
            if tile in SPECIAL_CHARACTERS:
                line += SPECIAL_CHARACTERS[tile]
            else:
                line += CHARACTERS[tile & 0x3F]
        lines.append(line.strip())
    return "\n".join(lines) + "\n"


# https://github.com/aaaaaa123456789/rtc3test
@pytest.mark.parametrize("subtest", [0, 1, 2])
def test_rtc3test(subtest, rtc3test_file):
    pyboy = PyBoy(rtc3test_file, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    for n in range(subtest):
        pyboy.button("down")
        pyboy.tick(2, True)

    pyboy.button("a")
    pyboy.tick(2, True)

    while True:
        # Continue until it says "(A) Return"
        if pyboy.tilemap_background[6:14, 17] == [193, 63, 27, 40, 55, 56, 53, 49]:
            break
        pyboy.tick(1, True)

    result = rtc3test_result(pyboy)
    with open(rtc3test_json, "r") as f:
        old_rtc3test = json.load(f)

    if OVERWRITE_JSON:
        with open(rtc3test_json, "w") as f:
            old_rtc3test[str(subtest)] = result
            json.dump(old_rtc3test, f, indent=4)
    else:
        assert result == old_rtc3test[str(subtest)], f"Outputs don't match for rtc3test subtest {subtest}"

    pyboy.stop(save=False)
