#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json

import pytest
from pytest_lazy_fixtures import lf

from pyboy import PyBoy

which_json = "tests/test_results/which.json"


def which_result(pyboy):
    lines = []
    for y in range(18):
        line = ""
        for tile in pyboy.tilemap_background[:20, y]:
            if tile == 256:
                line += " "
            elif 288 <= tile < 384:
                line += chr(tile - 256)
            else:
                raise ValueError(f"Unexpected which.gb tile value: {tile}")
        lines.append(line.rstrip())
    return "\n".join(lines).rstrip()


@pytest.mark.parametrize(
    "cgb, bootrom",
    [
        (False, None),
        (True, None),
        (False, lf("boot_rom")),
        (True, lf("boot_cgb_rom")),
    ],
    ids=("dmg_builtin", "cgb_builtin", "dmg_native", "cgb_native"),
)
def test_which(cgb, bootrom, which_file):
    pyboy = PyBoy(which_file, window="null", cgb=cgb, bootrom=bootrom)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(59, True)
        pyboy.tick(25, True)

        if bootrom is not None:
            pyboy.tick(400, True)

        result = which_result(pyboy)
    finally:
        pyboy.stop(save=False)

    with open(which_json, "r") as f:
        expected_results = json.load(f)
    result_key = f"{'cgb' if cgb else 'dmg'}_{'native' if bootrom is not None else 'builtin'}"
    expected = expected_results[result_key]
    assert result == expected, f"Outputs don't match for {result_key}"

    expected_cpu = "CGB" if cgb else "DMG"
    assert expected_cpu in result
