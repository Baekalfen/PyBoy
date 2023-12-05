from ..data.memory_addrs.game_state import GameStateAddress

class GameState():

    def __init__(self,
                 battle_type
                ):

        self._battle_type = battle_type

    def is_in_battle(self):
        return self._battle_type == 0
    
    @staticmethod
    def load_game_state(mem_manager):

        battle_type = mem_manager.read_hex_from_mem_address(GameStateAddress.BATTLE_TYPE.value)

        return GameState(battle_type)