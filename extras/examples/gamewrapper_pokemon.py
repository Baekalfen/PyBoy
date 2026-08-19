#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys

# Makes us able to import PyBoy from the directory below
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

from pyboy import PyBoy  # noqa

# Check if the ROM is given through argv
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python gamewrapper_pokemon.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(
    filename,
    window="null" if quiet else "SDL2",
    scale=3,
    debug=not quiet,
    sound_emulated=False,
)
pyboy.set_emulation_speed(0)

pokemon = pyboy.game_wrapper
pokemon.start_game()

pokemon.add_pokemon("CHARIZARD", level=10, moves=("WATERFALL",))
pokemon.add_pokemon("MEW", level=10)
print(pokemon.party)

# Set up the game state for trading and grant all badges.
pokemon.set_event_flag("got_pokedex")
for badge in ("boulder", "cascade", "thunder", "rainbow", "soul", "marsh", "volcano", "earth"):
    pokemon.set_badge(badge)

pokemon.warp("viridian_pokecenter")

pokemon.set_money(999999)
pokemon.set_item("MASTER_BALL", 255, force=True)  # Setting a glitched amount of Master balls

# https://bulbapedia.bulbagarden.net/wiki/%3F%3F%3F%3F%3F_(item_07)
pokemon.set_item("SURFBOARD", 1)  # Giving ourself the bugged item "surfboard"

# Example operations that can be enabled as needed:
# pokemon.remove_pokemon(5)
# pokemon.remove_pokemon(4)
# party = pokemon.party
# party[0]["level"] = 55
# pokemon.party = party
# pokemon.warp("name_raters_house")
# pokemon.start_wild_battle("PIKACHU", level=5)
# pokemon.start_trainer_battle("PROF_OAK", trainer_set=1)

pyboy.tick(50, False, False)

pyboy.set_emulation_speed(1)
while pyboy.tick():
    pass

pyboy.stop(save=False)
