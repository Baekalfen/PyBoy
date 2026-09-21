(plugins-reference)=
# Plugins and game wrappers

PyBoy selects a game wrapper from the cartridge title when one is available; otherwise it uses the generic wrapper. Access the selected wrapper through {attr}`pyboy.game_wrapper <pyboy.PyBoy.game_wrapper>`.

The wrappers expose game-specific state and controls in addition to the common game-area API. The Super Mario Bros. Deluxe wrapper supports world and level selection, Challenge mode, custom level sequences, CGB-aware tile mappings, and active-object data for automation and analysis.

The game-area debug view is enabled with `pyboy -d game_rom.gb`. Press **L** in the SDL2 window to cycle between the screen, mapped game-area, and text views. Wrappers can provide {meth}`game_area_annotations() <pyboy.plugins.base_plugin.PyBoyGameWrapper.game_area_annotations>` so object positions and other metadata are shown in the debug view.

```{toctree}
:maxdepth: 2

base_plugin
game_wrapper_super_mario_bros_deluxe
game_wrapper_super_mario_land
game_wrapper_tetris
game_wrapper_pandoras_blocks
game_wrapper_kirby_dream_land
game_wrapper_pokemon_gen1
game_wrapper_pokemon_pinball
game_wrapper2048
```
