#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy import PyBoy

# https://gitlab.com/BonsaiDen/vectroid.gb
# https://gitlab.com/BonsaiDen/vectroid.gb/-/jobs/artifacts/master/raw/build/vectroid.gbc?job=build_rom


def test_vectroid(vectroid_file):
    pyboy = PyBoy(vectroid_file, window="null")
    pyboy.tick(120, False, False)
    pyboy.button("start")
    pyboy.tick(120, False, False)
    assert pyboy.tilemap_background[3:17, 2] == [
        13,
        13,
        0,
        40,
        23,
        21,
        38,
        36,
        33,
        27,
        22,
        0,
        13,
        13,
    ], "Expected '-- vectroid --' title screen"
