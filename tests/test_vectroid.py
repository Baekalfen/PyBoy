#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy import PyBoy

# https://gitlab.com/BonsaiDen/vectroid.gb
# https://gitlab.com/BonsaiDen/vectroid.gb/-/jobs/artifacts/master/raw/build/vectroid.gbc?job=build_rom


def test_vectroid(vectroid_file):
    pyboy = PyBoy(vectroid_file, window="null")
    pyboy.tick(120, False)
    pyboy.screen.image
