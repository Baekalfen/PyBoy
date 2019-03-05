import PyBoy

P = PyBoy.PyBoy("SDL2", 1, "ROMs/pokemon_gold.gbc", "ROMs/DMG_ROM.bin")
# P = PyBoy.PyBoy("SDL2", 1, "ROMs/SuperMarioLand.gb", "ROMs/DMG_ROM.bin")

for n in range(1):
    P.tick()
# import pdb;pdb.set_trace()
